import json
import logging
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction, connection
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from qbosdk import exceptions as qbo_exc
from qbosdk import revoke_refresh_token

from fyle_rest_auth.utils import AuthUtils
from fyle_rest_auth.models import AuthToken
from fyle_rest_auth.helpers import get_fyle_admin

from fyle_integrations_platform_connector import PlatformConnector

from fyle_qbo_api.utils import assert_valid

from apps.quickbooks_online.utils import QBOConnector
from apps.fyle.helpers import get_cluster_domain
from fyle_accounting_mappings.models import ExpenseAttribute, DestinationAttribute

from .models import Workspace, FyleCredential, QBOCredential, WorkspaceGeneralSettings, LastExportDetail
from .utils import generate_qbo_refresh_token, create_or_update_general_settings
from .tasks import export_to_qbo
from .serializers import WorkspaceSerializer, QBOCredentialSerializer, \
    WorkSpaceGeneralSettingsSerializer, LastExportDetailSerializer
from .signals import post_delete_qbo_connection
from .permissions import IsAuthenticatedForTest

from apps.fyle.models import ExpenseGroupSettings

logger = logging.getLogger(__name__)
logger.level = logging.INFO

User = get_user_model()
auth_utils = AuthUtils()


class WorkspaceView(viewsets.ViewSet):
    """
    QBO Workspace
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a Workspace
        """

        access_token = request.META.get('HTTP_AUTHORIZATION')
        fyle_user = get_fyle_admin(access_token.split(' ')[1], None)
        org_name = fyle_user['data']['org']['name']
        org_id = fyle_user['data']['org']['id']
        org_currency = fyle_user['data']['org']['currency']

        workspace = Workspace.objects.filter(fyle_org_id=org_id).first()

        if workspace:
            workspace.user.add(User.objects.get(user_id=request.user))
            cache.delete(str(workspace.id))
        else:
            workspace = Workspace.objects.create(
                name=org_name, fyle_org_id=org_id, fyle_currency=org_currency, app_version='v2'
            )

            ExpenseGroupSettings.objects.create(workspace_id=workspace.id)

            LastExportDetail.objects.create(workspace_id=workspace.id)

            workspace.user.add(User.objects.get(user_id=request.user))

            auth_tokens = AuthToken.objects.get(user__user_id=request.user)

            cluster_domain = get_cluster_domain(auth_tokens.refresh_token)

            FyleCredential.objects.update_or_create(
                refresh_token=auth_tokens.refresh_token,
                workspace_id=workspace.id,
                cluster_domain=cluster_domain
            )

        return Response(
            data=WorkspaceSerializer(workspace).data,
            status=status.HTTP_200_OK
        )

    def get(self, request):
        """
        Get workspace
        """
        user = User.objects.get(user_id=request.user)
        org_id = request.query_params.get('org_id')
        workspace = Workspace.objects.filter(user__in=[user], fyle_org_id=org_id).all()

        return Response(
            data=WorkspaceSerializer(workspace, many=True).data,
            status=status.HTTP_200_OK
        )

    def get_by_id(self, request, **kwargs):
        """
        Get Workspace by id
        """
        try:
            user = User.objects.get(user_id=request.user)
            workspace = Workspace.objects.get(pk=kwargs['workspace_id'], user=user)

            return Response(
                data=WorkspaceSerializer(workspace).data if workspace else {},
                status=status.HTTP_200_OK
            )
        except Workspace.DoesNotExist:
            return Response(
                data={
                    'message': 'Workspace with this id does not exist'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, **kwargs):
        """
        PATCH workspace
        """
        workspace_instance = Workspace.objects.get(pk=kwargs['workspace_id'])
        serializer = WorkspaceSerializer(
            workspace_instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )


class ReadyView(viewsets.ViewSet):
    """
    Ready call
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """
        Ready call
        """
        Workspace.objects.first()

        return Response(
            data={
                'message': 'Ready'
            },
            status=status.HTTP_200_OK
        )


class ConnectQBOView(viewsets.ViewSet):
    """
    QBO Connect Oauth View
    """

    def post(self, request, **kwargs):
        # Extract data from the request
        authorization_code = request.data.get('code')
        realm_id = request.data.get('realm_id')
        redirect_uri = request.data.get('redirect_uri')

        try:
            # Generate a refresh token from the authorization code
            refresh_token = generate_qbo_refresh_token(authorization_code, redirect_uri)

            # Get the workspace associated with the request
            workspace = Workspace.objects.get(pk=kwargs['workspace_id'])

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
            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])
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

        except qbo_exc.UnauthorizedClientError:
            return Response({'message': 'Invalid Authorization Code'}, status=status.HTTP_401_UNAUTHORIZED)

        except qbo_exc.NotFoundClientError:
            return Response({'message': 'QBO Application not found'}, status=status.HTTP_404_NOT_FOUND)

        except qbo_exc.WrongParamsError as e:
            return Response(json.loads(e.response), status=status.HTTP_400_BAD_REQUEST)

        except qbo_exc.InternalServerError:
            return Response({'message': 'Wrong/Expired Authorization code'}, status=status.HTTP_401_UNAUTHORIZED)


    def patch(self, request, **kwargs):
        """Delete QBO refresh_token"""
        workspace_id = kwargs['workspace_id']
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

    def get(self, request, **kwargs):
        """
        Get QBO Credentials in Workspace
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace=kwargs['workspace_id'], is_expired=False)

            return Response(
                data=QBOCredentialSerializer(qbo_credentials).data,
                status=status.HTTP_200_OK if qbo_credentials.refresh_token else status.HTTP_400_BAD_REQUEST
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO Credentials not found in this workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class GeneralSettingsView(viewsets.ViewSet):
    """
    General Settings
    """
    serializer_class = WorkSpaceGeneralSettingsSerializer
    queryset = WorkspaceGeneralSettings.objects.all()

    def post(self, request, *args, **kwargs):
        """
        Post workspace general settings
        """
        general_settings_payload = request.data
        assert_valid(general_settings_payload is not None, 'Request body is empty')

        workspace_id = kwargs['workspace_id']

        general_settings = create_or_update_general_settings(general_settings_payload, workspace_id)

        return Response(
            data=self.serializer_class(general_settings).data,
            status=status.HTTP_200_OK
        )

    def get(self, request, *args, **kwargs):
        """
        Get workspace general settings
        """
        try:
            general_settings = self.queryset.get(workspace_id=kwargs['workspace_id'])
            return Response(
                data=self.serializer_class(general_settings).data,
                status=status.HTTP_200_OK
            )
        except WorkspaceGeneralSettings.DoesNotExist:
            return Response(
                {
                    'message': 'General Settings does not exist in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, **kwargs):
        """
        PATCH workspace general settings
        """
        workspace_general_settings_object = WorkspaceGeneralSettings.objects.get(workspace_id=kwargs['workspace_id'])
        serializer = WorkSpaceGeneralSettingsSerializer(
            workspace_general_settings_object, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )


class ExportToQBOView(viewsets.ViewSet):
    """
    Export Expenses to QBO
    """

    def post(self, request, *args, **kwargs):
        export_to_qbo(workspace_id=kwargs['workspace_id'])

        return Response(
            status=status.HTTP_200_OK
        )


class LastExportDetailView(viewsets.ViewSet):
    """
    Last Export Details
    """
    serializer_class = LastExportDetailSerializer

    def get(self, request, *args, **kwargs):
        """
        last export detail
        """
        last_export_detail = LastExportDetail.objects.filter(workspace_id=kwargs['workspace_id']).first()
        if last_export_detail.last_exported_at and last_export_detail.total_expense_groups_count:
            return Response(
                data=self.serializer_class(last_export_detail).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={
                    'message': 'latest exported details does not exist in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
class WorkspaceAdminsView(viewsets.ViewSet):

    def get(self, request, *args, **kwargs):
        """
        Get Admins for the workspaces
        """

        workspace = Workspace.objects.get(pk=kwargs['workspace_id'])
        
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

        return Response(
                data=admin_email,
                status=status.HTTP_200_OK
            )

class SetupE2ETestView(viewsets.ViewSet):
    """
    QBO Workspace
    """
    authentication_classes = []
    permission_classes = [IsAuthenticatedForTest]

    def post(self, request, **kwargs):
        """
        Setup end to end test for a given workspace
        """
        try:
            workspace = Workspace.objects.get(pk=kwargs['workspace_id'])
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
                            QBOCredential.objects.create(
                                workspace=workspace,
                                refresh_token=qbo_connector.connection.refresh_token,
                                realm_id=healthy_token.realm_id,
                                is_expired=False,
                                company_name=healthy_token.company_name,
                                country=healthy_token.country
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
            logger.error(error)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': error_message})
