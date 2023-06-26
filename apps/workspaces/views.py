import json
import logging
from datetime import datetime
from rest_framework import generics

from django_filters.rest_framework import DjangoFilterBackend

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
from fyle_qbo_api.utils import LookupFieldMixin
from fyle_accounting_mappings.models import ExpenseAttribute, DestinationAttribute

from .models import Workspace, FyleCredential, QBOCredential, WorkspaceGeneralSettings, LastExportDetail
from .utils import generate_qbo_refresh_token, create_or_update_general_settings
from .tasks import export_to_qbo
from .serializers import WorkspaceSerializer, QBOCredentialSerializer, \
    WorkSpaceGeneralSettingsSerializer, LastExportDetailSerializer
from .signals import post_delete_qbo_connection
from .permissions import IsAuthenticatedForTest
from apps.exceptions import handle_view_exceptions

from apps.fyle.models import ExpenseGroupSettings
from .actions import update_or_create_workspace, connect_qbo_oauth, get_workspace_admin

logger = logging.getLogger(__name__)
logger.level = logging.INFO

User = get_user_model()
auth_utils = AuthUtils()


class WorkspaceView(generics.CreateAPIView, generics.RetrieveAPIView, generics.ListAPIView, generics.UpdateAPIView):
    """
    QBO Workspace
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a Workspace
        """
        access_token = request.META.get('HTTP_AUTHORIZATION')
        user = request.user
        fyle_user = get_fyle_admin(access_token.split(' ')[1], None)
        workspace = update_or_create_workspace(user, 
                                  org_id=fyle_user['data']['org']['id'], 
                                  org_name=fyle_user['data']['org']['name'], 
                                  org_currency=fyle_user['data']['org']['currency'])
       
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


class ReadyView(generics.ListAPIView):
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


class ConnectQBOView(generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView):
    """
    QBO Connect Oauth View
    """

    def post(self, request, **kwargs):
        authorization_code = request.data.get('code')
        realm_id = request.data.get('realm_id')
        redirect_uri = request.data.get('redirect_uri')
        try:
            # Generate a refresh token from the authorization code
            refresh_token = generate_qbo_refresh_token(authorization_code, redirect_uri)
            return connect_qbo_oauth(refresh_token, realm_id, kwargs['workspace_id'])
        except (qbo_exc.UnauthorizedClientError, qbo_exc.NotFoundClientError, qbo_exc.WrongParamsError, qbo_exc.InternalServerError) as e:
            logger.info('Invalid/Expired Authorization Code or QBO application not found - %s',{'error': e.response})
            return Response({'message': 'Invalid/Expired Authorization Code or QBO application not found'}, status=status.HTTP_401_UNAUTHORIZED)


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

    @handle_view_exceptions()
    def get(self, request, **kwargs):
        """
        Get QBO Credentials in Workspace
        """
        qbo_credentials = QBOCredential.objects.get(workspace=kwargs['workspace_id'], is_expired=False)

        return Response(
            data=QBOCredentialSerializer(qbo_credentials).data,
            status=status.HTTP_200_OK if qbo_credentials.refresh_token else status.HTTP_400_BAD_REQUEST
        )


class GeneralSettingsView(LookupFieldMixin, generics.ListAPIView):
    """
    General Settings
    """
    queryset = WorkspaceGeneralSettings.objects.all()
    serializer_class = WorkSpaceGeneralSettingsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = { 'workspace_id': {'exact'} }

class ExportToQBOView(generics.CreateAPIView):
    """
    Export Expenses to QBO
    """

    def post(self, request, *args, **kwargs):
        export_to_qbo(workspace_id=kwargs['workspace_id'])

        return Response(
            status=status.HTTP_200_OK
        )


class LastExportDetailView(generics.RetrieveAPIView):
    """
    Last Export Details
    """
    queryset = LastExportDetail.objects.first()
    serializer_class = LastExportDetailSerializer
    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'


class WorkspaceAdminsView(generics.RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        """
        Get Admins for the workspaces
        """
        admin_email = get_workspace_admin(kwargs['workspace_id'])
        
        return Response(
                data=admin_email,
                status=status.HTTP_200_OK
            )

class SetupE2ETestView(generics.CreateAPIView):
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
            logger.error(error)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': error_message})
