import logging
from datetime import datetime

from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework.response import Response
from qbosdk import revoke_refresh_token
from rest_framework.views import status
from fyle_accounting_mappings.models import ExpenseAttribute, DestinationAttribute
from fyle_rest_auth.models import AuthToken
from fyle_integrations_platform_connector import PlatformConnector

from fyle_rest_auth.helpers import get_fyle_admin

from apps.quickbooks_online.utils import QBOConnector
from apps.fyle.models import ExpenseGroupSettings
from apps.fyle.helpers import get_cluster_domain

from .models import Workspace, LastExportDetail, FyleCredential, QBOCredential
from .utils import assert_valid
from .serializers import QBOCredentialSerializer
from .signals import post_delete_qbo_connection


User = get_user_model()
logger = logging.getLogger(__name__)
logger.level = logging.INFO

def update_or_create_workspace(user, access_token):
    fyle_user = get_fyle_admin(access_token.split(' ')[1], None)
    org_id=fyle_user['data']['org']['id']
    org_name=fyle_user['data']['org']['name']
    org_currency=fyle_user['data']['org']['currency']
    workspace = Workspace.objects.filter(fyle_org_id=org_id).first()

    if workspace:
        workspace.user.add(User.objects.get(user_id=user))
        cache.delete(str(workspace.id))
    else:
        workspace = Workspace.objects.create(
            name=org_name, fyle_org_id=org_id, fyle_currency=org_currency, app_version='v2'
        )

        ExpenseGroupSettings.objects.create(workspace_id=workspace.id)

        LastExportDetail.objects.create(workspace_id=workspace.id)

        workspace.user.add(User.objects.get(user_id=user))

        auth_tokens = AuthToken.objects.get(user__user_id=user)

        cluster_domain = get_cluster_domain(auth_tokens.refresh_token)

        FyleCredential.objects.update_or_create(
            refresh_token=auth_tokens.refresh_token,
            workspace_id=workspace.id,
            cluster_domain=cluster_domain
        )
    return workspace

def connect_qbo_oauth(refresh_token, realm_id, workspace_id):
    # Get the workspace associated with the request
    workspace = Workspace.objects.get(pk=workspace_id)

    # Get the QBO credentials associated with the workspace, or create new credentials if none exist
    qbo_credentials = QBOCredential.objects.filter(workspace=workspace).first()
    if not qbo_credentials:
        qbo_credentials = QBOCredential.objects.create(
            refresh_token=refresh_token,
            realm_id=realm_id,
            workspace=workspace
        )

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
        workspace.onboarding_state = 'MAP_EMPLOYEES'
    workspace.save()

    # Return the QBO credentials as serialized data
    return Response(data=QBOCredentialSerializer(qbo_credentials).data, status=status.HTTP_200_OK)


def get_workspace_admin(workspace_id: int):
    workspace = Workspace.objects.get(pk=workspace_id)

    admin_email = []
    users = workspace.user.all()
    for user in users:
        admin = User.objects.get(user_id=user)
        name = ExpenseAttribute.objects.get(
            value=admin.email,
            workspace_id=workspace_id,
            attribute_type='EMPLOYEE'
        ).detail['full_name']

        admin_email.append({
            'name': name,
            'email': admin.email
        })
    return admin_email

def delete_qbo_refresh_token(workspace_id: int):
    qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
    refresh_token = qbo_credentials.refresh_token
    qbo_credentials.refresh_token = None
    qbo_credentials.is_expired = False
    qbo_credentials.realm_id = None
    qbo_credentials.save()
    
    post_delete_qbo_connection(workspace_id)

    try:
        revoke_refresh_token(refresh_token, settings.QBO_CLIENT_ID, settings.QBO_CLIENT_SECRET)
    except Exception as exception:
        logger.error(exception)
        pass

    return Response(data={
        'workspace_id': workspace_id,
        'message': 'QBO Refresh Token deleted'
    })


def setup_e2e_tests(workspace_id: int, connection):
    try:
        workspace = Workspace.objects.get(pk=workspace_id)
        error_message = 'Something unexpected has happened. Please try again later.'

        # Filter out prod orgs
        if 'fyle for' in workspace.name.lower():
            # Grab the latest healthy refresh token, from a demo org with the specified realm id
            healthy_tokens = QBOCredential.objects.filter(
                workspace__name__icontains='fyle for',
                is_expired=False,
                realm_id=settings.E2E_TESTS_REALM_ID,
                refresh_token__isnull=False
            ).order_by('-updated_at')
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
                            workspace=workspace,
                            defaults = {
                                'refresh_token' : qbo_connector.connection.refresh_token,
                                'realm_id' : healthy_token.realm_id,
                                'is_expired' : False,
                                'company_name' : healthy_token.company_name,
                                'country' : healthy_token.country
                            }
                        )

                        # Sync dimension for QBO and Fyle
                        qbo_connector.sync_dimensions()

                        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace.id)
                        platform = PlatformConnector(fyle_credentials)
                        platform.import_fyle_dimensions(import_taxes=True)

                        # Reset workspace details
                        workspace.onboarding_state = 'MAP_EMPLOYEES'
                        workspace.source_synced_at = datetime.now()
                        workspace.destination_synced_at = datetime.now()
                        workspace.qbo_realm_id = healthy_token.realm_id
                        workspace.last_synced_at = None
                        workspace.save()

                        #insert a destination attribute
                        DestinationAttribute.create_or_update_destination_attribute({
                            'attribute_type': 'ACCOUNT',
                            'display_name': 'Account',
                            'value': 'Activity',
                            'destination_id': '900',
                            'active': True,
                            'detail': {"account_type": "Expense", "fully_qualified_name": "Activity"}
                        }, workspace.id)

                        return Response(status=status.HTTP_200_OK)

            error_message = 'No healthy tokens found, please try again later.'
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': error_message})

    except Exception as error:
        error_message = 'No healthy tokens found, please try again later.'
        logger.error(error)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': error_message})
    

    