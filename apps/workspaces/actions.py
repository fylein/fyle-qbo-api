import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django_q.tasks import async_task
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute
from fyle_integrations_platform_connector import PlatformConnector
from fyle_rest_auth.helpers import get_fyle_admin
from fyle_rest_auth.models import AuthToken
from qbosdk import revoke_refresh_token
from rest_framework.response import Response
from rest_framework.views import status

from apps.fyle.actions import update_failed_expenses
from apps.fyle.helpers import get_cluster_domain, patch_request, post_request
from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.fyle.queue import async_post_accounting_export_summary
from apps.quickbooks_online.queue import (
    schedule_bills_creation,
    schedule_cheques_creation,
    schedule_credit_card_purchase_creation,
    schedule_journal_entry_creation,
    schedule_qbo_expense_creation,
)
from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import (
    FyleCredential,
    LastExportDetail,
    QBOCredential,
    Workspace,
    WorkspaceGeneralSettings,
    WorkspaceSchedule,
)
from apps.workspaces.serializers import QBOCredentialSerializer
from apps.workspaces.signals import post_delete_qbo_connection
from fyle_qbo_api.utils import assert_valid

User = get_user_model()
logger = logging.getLogger(__name__)
logger.level = logging.INFO


def update_or_create_workspace(user, access_token):
    fyle_user = get_fyle_admin(access_token.split(' ')[1], None)
    org_id = fyle_user['data']['org']['id']
    org_name = fyle_user['data']['org']['name']
    org_currency = fyle_user['data']['org']['currency']
    workspace = Workspace.objects.filter(fyle_org_id=org_id).first()

    if workspace:
        workspace.user.add(User.objects.get(user_id=user))
        workspace.name = org_name
        workspace.save()
        cache.delete(str(workspace.id))
    else:
        workspace = Workspace.objects.create(name=org_name, fyle_org_id=org_id, fyle_currency=org_currency, app_version='v2')

        ExpenseGroupSettings.objects.create(workspace_id=workspace.id)

        LastExportDetail.objects.create(workspace_id=workspace.id)

        workspace.user.add(User.objects.get(user_id=user))

        auth_tokens = AuthToken.objects.get(user__user_id=user)

        cluster_domain = get_cluster_domain(auth_tokens.refresh_token)

        FyleCredential.objects.update_or_create(refresh_token=auth_tokens.refresh_token, workspace_id=workspace.id, cluster_domain=cluster_domain)
        async_task('apps.workspaces.tasks.async_add_admins_to_workspace', workspace.id, user.user_id)

    return workspace


def connect_qbo_oauth(refresh_token, realm_id, workspace_id):
    # Get the workspace associated with the request
    workspace = Workspace.objects.get(pk=workspace_id)

    # Get the QBO credentials associated with the workspace, or create new credentials if none exist
    qbo_credentials = QBOCredential.objects.filter(workspace=workspace).first()
    if not qbo_credentials:
        qbo_credentials = QBOCredential.objects.create(refresh_token=refresh_token, realm_id=realm_id, workspace=workspace)

    # Check if the realm_id matches the one associated with the workspace
    if workspace.qbo_realm_id:
        assert_valid(realm_id == workspace.qbo_realm_id, 'Please choose the correct QuickBooks Online account')

    # Update the workspace with the realm_id and refresh_token
    qbo_credentials.is_expired = False
    qbo_credentials.refresh_token = refresh_token
    qbo_credentials.realm_id = realm_id
    qbo_credentials.save()

    # Use the QBO credentials to get the company info and preferences
    qbo_connector = QBOConnector(qbo_credentials, workspace_id=workspace_id)
    company_info = qbo_connector.get_company_info()
    preferences = qbo_connector.get_company_preference()

    # Update the QBO credentials with the retrieved company info and preferences
    qbo_credentials.country = company_info['Country']
    qbo_credentials.company_name = company_info['CompanyName']
    qbo_credentials.currency = preferences['CurrencyPrefs']['HomeCurrency']['value']

    qbo_credentials.save()

    # Update the workspace onboarding state and realm_id
    workspace.qbo_realm_id = realm_id

    if workspace.onboarding_state == 'CONNECTION':
        workspace.onboarding_state = 'EXPORT_SETTINGS'
        if settings.BRAND_ID == 'co':
            workspace_general_settings_instance = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace.id).first()
            if not workspace_general_settings_instance:
                WorkspaceGeneralSettings.objects.update_or_create(
                    workspace_id=workspace_id, defaults={'employee_field_mapping': 'VENDOR', 'auto_map_employees': None}
                )

    workspace.save()

    if workspace.onboarding_state == 'COMPLETE':
        post_to_integration_settings(workspace_id, True)

    # Return the QBO credentials as serialized data
    return Response(data=QBOCredentialSerializer(qbo_credentials).data, status=status.HTTP_200_OK)


def get_workspace_admin(workspace_id: int):
    workspace = Workspace.objects.get(pk=workspace_id)

    admin_email = []
    users = workspace.user.all()
    for user in users:
        admin = User.objects.get(user_id=user)
        employee = ExpenseAttribute.objects.filter(value=admin.email, workspace_id=workspace_id, attribute_type='EMPLOYEE').first()
        if employee:
            admin_email.append({'name': employee.detail['full_name'], 'email': admin.email})

    return admin_email


def delete_qbo_refresh_token(workspace_id: int):
    qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
    refresh_token = qbo_credentials.refresh_token
    qbo_credentials.refresh_token = None
    qbo_credentials.is_expired = False
    qbo_credentials.realm_id = None
    qbo_credentials.save()

    post_delete_qbo_connection(workspace_id)

    post_to_integration_settings(workspace_id, False)

    try:
        revoke_refresh_token(refresh_token, settings.QBO_CLIENT_ID, settings.QBO_CLIENT_SECRET)
    except Exception as exception:
        logger.error(exception)
        pass

    return Response(data={'workspace_id': workspace_id, 'message': 'QBO Refresh Token deleted'})


def setup_e2e_tests(workspace_id: int, connection):
    try:
        workspace = Workspace.objects.get(pk=workspace_id)
        error_message = 'Something unexpected has happened. Please try again later.'

        # Filter out prod orgs
        if 'fyle for' in workspace.name.lower():
            # Grab the latest healthy refresh token, from a demo org with the specified realm id
            healthy_tokens = QBOCredential.objects.filter(workspace__name__icontains='fyle for', is_expired=False, realm_id=settings.E2E_TESTS_REALM_ID, refresh_token__isnull=False).order_by('-updated_at')
            logger.info('Found {} healthy tokens'.format(healthy_tokens.count()))

            for healthy_token in healthy_tokens:
                logger.info('Checking token health for workspace: {}'.format(healthy_token.workspace_id))
                # Token Health check
                try:
                    qbo_connector = QBOConnector(healthy_token, workspace_id=workspace.id)
                    qbo_connector.get_company_preference()
                    logger.info('Yaay, token is healthly for workspace: {}'.format(healthy_token.workspace_id))
                except Exception:
                    # If the token is expired, setting is_expired = True so that they are not used for future runs
                    logger.info('Oops, token is dead for workspace: {}'.format(healthy_token.workspace_id))
                    healthy_token.is_expired = True
                    healthy_token.save()
                    # Stop the execution here for the token since it's expired
                    continue

                with transaction.atomic():
                    if healthy_token:
                        # Reset the workspace completely
                        with connection.cursor() as cursor:
                            cursor.execute('select reset_workspace(%s)', [workspace.id])

                        # Store the latest healthy refresh token for the workspace
                        QBOCredential.objects.update_or_create(
                            workspace=workspace, defaults={'refresh_token': qbo_connector.connection.refresh_token, 'realm_id': healthy_token.realm_id, 'is_expired': False, 'company_name': healthy_token.company_name, 'country': healthy_token.country}
                        )

                        # Sync dimension for QBO and Fyle
                        qbo_connector.sync_dimensions()

                        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace.id)
                        platform = PlatformConnector(fyle_credentials)
                        platform.import_fyle_dimensions(import_taxes=True)

                        # Reset workspace details
                        workspace.onboarding_state = 'EXPORT_SETTINGS'
                        workspace.source_synced_at = datetime.now()
                        workspace.destination_synced_at = datetime.now()
                        workspace.qbo_realm_id = healthy_token.realm_id
                        workspace.last_synced_at = None
                        workspace.save()

                        # insert a destination attribute
                        DestinationAttribute.create_or_update_destination_attribute(
                            {'attribute_type': 'ACCOUNT', 'display_name': 'Account', 'value': 'Activity', 'destination_id': '900', 'active': True, 'detail': {"account_type": "Expense", "fully_qualified_name": "Activity"}}, workspace.id
                        )

                        return Response(status=status.HTTP_200_OK)

            error_message = 'No healthy tokens found, please try again later.'
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': error_message})

    except Exception as error:
        error_message = 'No healthy tokens found, please try again later.'
        logger.error(error)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': error_message})


def post_to_integration_settings(workspace_id: int, active: bool):
    """
    Post to integration settings
    """
    refresh_token = FyleCredential.objects.get(workspace_id=workspace_id).refresh_token
    url = '{}/integrations/'.format(settings.INTEGRATIONS_SETTINGS_API)
    payload = {
        'tpa_id': settings.FYLE_CLIENT_ID,
        'tpa_name': 'Fyle Quickbooks Integration',
        'type': 'ACCOUNTING',
        'is_active': active,
        'connected_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    try:
        post_request(url, payload, refresh_token)
    except Exception as error:
        logger.error(error)


def patch_integration_settings(workspace_id: int, errors: int = None, is_token_expired = None):
    """
    Patch integration settings
    """

    refresh_token = FyleCredential.objects.get(workspace_id=workspace_id).refresh_token
    url = '{}/integrations/'.format(settings.INTEGRATIONS_SETTINGS_API)
    payload = {
        'tpa_name': 'Fyle Quickbooks Integration',
    }

    if errors is not None:
        payload['errors_count'] = errors

    if is_token_expired is not None:
        payload['is_token_expired'] = is_token_expired

    try:
        patch_request(url, payload, refresh_token)
    except Exception as error:
        logger.error(error, exc_info=True)


def export_to_qbo(workspace_id, export_mode=None, expense_group_ids=[], is_direct_export:bool = False):
    active_qbo_credentials = QBOCredential.objects.filter(
        workspace_id=workspace_id,
        is_expired=False,
        refresh_token__isnull=False
    ).first()

    if not active_qbo_credentials:
        if is_direct_export:
            failed_expense_ids = []
            for expense_group_id in expense_group_ids:
                expense_group = ExpenseGroup.objects.get(id=expense_group_id)
                update_failed_expenses(expense_group.expenses.all(), False)
                failed_expense_ids.extend(expense_group.expenses.values_list('id', flat=True))
            async_post_accounting_export_summary(expense_group.workspace.fyle_org_id, workspace_id, failed_expense_ids, True)
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    workspace_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id, interval_hours__gt=0, enabled=True).first()
    last_exported_at = datetime.now()
    is_expenses_exported = False
    export_mode = export_mode or 'MANUAL'
    expense_group_filters = {
        'exported_at__isnull': True,
        'workspace_id': workspace_id
    }
    if expense_group_ids:
        expense_group_filters['id__in'] = expense_group_ids

    if general_settings.reimbursable_expenses_object:
        expense_group_ids = ExpenseGroup.objects.filter(fund_source='PERSONAL', **expense_group_filters).values_list('id', flat=True)

        if len(expense_group_ids):
            is_expenses_exported = True

        if general_settings.reimbursable_expenses_object == 'BILL':
            schedule_bills_creation(
                workspace_id=workspace_id,
                expense_group_ids=expense_group_ids,
                is_auto_export=export_mode == 'AUTO',
                fund_source='PERSONAL',
                interval_hours=workspace_schedule.interval_hours if workspace_schedule else 0
            )

        elif general_settings.reimbursable_expenses_object == 'EXPENSE':
            schedule_qbo_expense_creation(
                workspace_id=workspace_id,
                expense_group_ids=expense_group_ids,
                is_auto_export=export_mode == 'AUTO',
                fund_source='PERSONAL',
                interval_hours=workspace_schedule.interval_hours if workspace_schedule else 0
            )

        elif general_settings.reimbursable_expenses_object == 'CHECK':
            schedule_cheques_creation(
                workspace_id=workspace_id,
                expense_group_ids=expense_group_ids,
                is_auto_export=export_mode == 'AUTO',
                fund_source='PERSONAL',
                interval_hours=workspace_schedule.interval_hours if workspace_schedule else 0
            )

        elif general_settings.reimbursable_expenses_object == 'JOURNAL ENTRY':
            schedule_journal_entry_creation(
                workspace_id=workspace_id,
                expense_group_ids=expense_group_ids,
                is_auto_export=export_mode == 'AUTO',
                fund_source='PERSONAL',
                interval_hours=workspace_schedule.interval_hours if workspace_schedule else 0
            )

    if general_settings.corporate_credit_card_expenses_object:
        expense_group_ids = ExpenseGroup.objects.filter(fund_source='CCC', **expense_group_filters).values_list('id', flat=True)

        if len(expense_group_ids):
            is_expenses_exported = True

        if general_settings.corporate_credit_card_expenses_object == 'JOURNAL ENTRY':
            schedule_journal_entry_creation(
                workspace_id=workspace_id,
                expense_group_ids=expense_group_ids,
                is_auto_export=export_mode == 'AUTO',
                fund_source='CCC',
                interval_hours=workspace_schedule.interval_hours if workspace_schedule else 0
            )

        elif general_settings.corporate_credit_card_expenses_object == 'CREDIT CARD PURCHASE':
            schedule_credit_card_purchase_creation(
                workspace_id=workspace_id,
                expense_group_ids=expense_group_ids,
                is_auto_export=export_mode == 'AUTO',
                fund_source='CCC',
                interval_hours=workspace_schedule.interval_hours if workspace_schedule else 0
            )

        elif general_settings.corporate_credit_card_expenses_object == 'DEBIT CARD EXPENSE':
            schedule_qbo_expense_creation(
                workspace_id=workspace_id,
                expense_group_ids=expense_group_ids,
                is_auto_export=export_mode == 'AUTO',
                fund_source='CCC',
                interval_hours=workspace_schedule.interval_hours if workspace_schedule else 0
            )

        elif general_settings.corporate_credit_card_expenses_object == 'BILL':
            schedule_bills_creation(
                workspace_id=workspace_id,
                expense_group_ids=expense_group_ids,
                is_auto_export=export_mode == 'AUTO',
                fund_source='CCC',
                interval_hours=workspace_schedule.interval_hours if workspace_schedule else 0
            )
    if is_expenses_exported:
        last_export_detail.last_exported_at = last_exported_at
        last_export_detail.export_mode = export_mode

        if workspace_schedule:
            last_export_detail.next_export_at = last_exported_at + timedelta(hours=workspace_schedule.interval_hours)

        last_export_detail.save()
