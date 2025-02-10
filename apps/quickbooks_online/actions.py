import logging
from datetime import datetime, timezone

from django.conf import settings
from django.db.models import Q
from apps.workspaces.actions import patch_integration_settings
from django_q.tasks import Chain
from fyle_accounting_mappings.models import MappingSetting
from qbosdk.exceptions import InvalidTokenError, WrongParamsError
from rest_framework.response import Response
from rest_framework.views import status

from apps.fyle.actions import update_complete_expenses
from apps.fyle.models import ExpenseGroup
from apps.fyle.tasks import post_accounting_export_summary
from apps.mappings.constants import SYNC_METHODS
from apps.mappings.helpers import get_auto_sync_permission
from apps.quickbooks_online.helpers import generate_export_type_and_id
from apps.quickbooks_online.utils import QBOConnector
from apps.tasks.models import TaskLog
from apps.workspaces.models import LastExportDetail, QBOCredential, Workspace, WorkspaceGeneralSettings

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def update_last_export_details(workspace_id):
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)

    failed_exports = TaskLog.objects.filter(~Q(type='CREATING_BILL_PAYMENT'), workspace_id=workspace_id, status__in=['FAILED', 'FATAL']).count()

    successful_exports = TaskLog.objects.filter(~Q(type__in=['CREATING_BILL_PAYMENT', 'FETCHING_EXPENSES']), workspace_id=workspace_id, status='COMPLETE', updated_at__gt=last_export_detail.last_exported_at).count()

    last_export_detail.failed_expense_groups_count = failed_exports
    last_export_detail.successful_expense_groups_count = successful_exports
    last_export_detail.total_expense_groups_count = failed_exports + successful_exports
    last_export_detail.save()

    patch_integration_settings(workspace_id, errors=failed_exports)

    return last_export_detail


def get_preferences(workspace_id: int):
    try:
        qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)

        qbo_connector = QBOConnector(qbo_credentials, workspace_id=workspace_id)

        preferences = qbo_connector.get_company_preference()

        return Response(data=preferences, status=status.HTTP_200_OK)
    except QBOCredential.DoesNotExist:
        return Response(data={'message': 'QBO credentials not found in workspace'}, status=status.HTTP_400_BAD_REQUEST)
    except (WrongParamsError, InvalidTokenError):
        if qbo_credentials:
            if not qbo_credentials.is_expired:
                patch_integration_settings(workspace_id, is_token_expired=True)
            qbo_credentials.refresh_token = None
            qbo_credentials.is_expired = True
            qbo_credentials.save()

        return Response(data={'message': 'Invalid token or Quickbooks Online connection expired'}, status=status.HTTP_400_BAD_REQUEST)


def refresh_quickbooks_dimensions(workspace_id: int):
    quickbooks_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    quickbooks_connector = QBOConnector(quickbooks_credentials, workspace_id=workspace_id)

    mapping_settings = MappingSetting.objects.filter(workspace_id=workspace_id, import_to_fyle=True)
    credentials = QBOCredential.objects.get(workspace_id=workspace_id)
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()

    chain = Chain()

    if workspace_general_settings:
        for mapping_setting in mapping_settings:
            if mapping_setting.source_field in ['PROJECT', 'COST_CENTER'] or mapping_setting.is_custom:
                chain.append(
                    'fyle_integrations_imports.tasks.trigger_import_via_schedule',
                    workspace_id,
                    mapping_setting.destination_field,
                    mapping_setting.source_field,
                    'apps.quickbooks_online.utils.QBOConnector',
                    credentials,
                    [SYNC_METHODS[mapping_setting.destination_field]],
                    get_auto_sync_permission(workspace_general_settings, mapping_setting),
                    False,
                    None,
                    mapping_setting.is_custom,
                    q_options={'cluster': 'import'}
                )

        if workspace_general_settings.import_tax_codes:
            chain.append(
                'fyle_integrations_imports.tasks.trigger_import_via_schedule',
                workspace_id,
                'TAX_CODE',
                'TAX_GROUP',
                'apps.quickbooks_online.utils.QBOConnector',
                credentials,
                [SYNC_METHODS['TAX_CODE']],
                False,
                False,
                None,
                False,
                q_options={'cluster': 'import'}
            )

        if workspace_general_settings.import_categories or workspace_general_settings.import_items:
            destination_sync_methods = []
            if workspace_general_settings.import_categories:
                destination_sync_methods.append(SYNC_METHODS['ACCOUNT'])
            if workspace_general_settings.import_items:
                destination_sync_methods.append(SYNC_METHODS['ITEM'])

            chain.append(
                'fyle_integrations_imports.tasks.trigger_import_via_schedule',
                workspace_id,
                'ACCOUNT',
                'CATEGORY',
                'apps.quickbooks_online.utils.QBOConnector',
                credentials,
                destination_sync_methods,
                get_auto_sync_permission(workspace_general_settings, None),
                False,
                workspace_general_settings.charts_of_accounts if 'accounts' in destination_sync_methods else None,
                False,
                True,
                True if 'ACCOUNT' in workspace_general_settings.import_code_fields else False,
                q_options={'cluster': 'import'}
            )

        if workspace_general_settings.import_vendors_as_merchants:
            chain.append(
                'fyle_integrations_imports.tasks.trigger_import_via_schedule',
                workspace_id,
                'VENDOR',
                'MERCHANT',
                'apps.quickbooks_online.utils.QBOConnector',
                credentials,
                [SYNC_METHODS['VENDOR']],
                False,
                False,
                None,
                False,
                q_options={'cluster': 'import'}
            )

    if chain.length() > 0:
        chain.run()

    quickbooks_connector.sync_dimensions()

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.destination_synced_at = datetime.now()
    workspace.save(update_fields=['destination_synced_at'])


def sync_quickbooks_dimensions(workspace_id: int):
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.destination_synced_at:
        time_interval = datetime.now(timezone.utc) - workspace.destination_synced_at

    if workspace.destination_synced_at is None or time_interval.days > 0:
        quickbooks_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
        quickbooks_connector = QBOConnector(quickbooks_credentials, workspace_id=workspace_id)
        quickbooks_connector.sync_dimensions()

        workspace.destination_synced_at = datetime.now()
        workspace.save(update_fields=['destination_synced_at'])


def generate_export_url_and_update_expense(expense_group: ExpenseGroup) -> None:
    """
    Generate export url and update expense
    :param expense_group: Expense Group
    :return: None
    """
    try:
        export_type, export_id = generate_export_type_and_id(expense_group)
        url = '{qbo_app_url}/app/{export_type}?txnId={export_id}'.format(
            qbo_app_url=settings.QBO_APP_URL,
            export_type=export_type,
            export_id=export_id
        )

    except Exception as error:
        # Defaulting it to QBO app url, worst case scenario if we're not able to parse it properly
        url = settings.QBO_APP_URL
        logger.error('Error while generating export url %s', error)

    expense_group.export_url = url
    expense_group.save()

    update_complete_expenses(expense_group.expenses.all(), url)
    post_accounting_export_summary(expense_group.workspace.fyle_org_id, expense_group.workspace.id, [expense.id for expense in expense_group.expenses.all()], expense_group.fund_source)
