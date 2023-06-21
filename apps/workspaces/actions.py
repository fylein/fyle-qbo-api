from rest_framework.response import Response
from rest_framework.views import status
from qbosdk import exceptions as qbo_exc

from django.contrib.auth import get_user_model
from django.core.cache import cache

from fyle_rest_auth.helpers import get_fyle_admin
from apps.fyle.helpers import get_cluster_domain
from fyle_rest_auth.models import AuthToken

from apps.quickbooks_online.utils import QBOConnector
from .models import Workspace, LastExportDetail, FyleCredential, QBOCredential
from fyle_accounting_mappings.models import ExpenseAttribute
from apps.fyle.models import ExpenseGroupSettings
from .utils import generate_qbo_refresh_token, assert_valid
from .serializers import WorkspaceSerializer, QBOCredentialSerializer, \
    WorkSpaceGeneralSettingsSerializer, LastExportDetailSerializer
from .signals import post_delete_qbo_connection


User = get_user_model()

def qbo_workspace(user, org_id, org_name, org_currency):
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
            workspace_id=kwargs['workspace_id'],
            attribute_type='EMPLOYEE'
        ).detail['full_name']

        admin_email.append({
            'name': name,
            'email': admin.email
        })
    return admin_email

    