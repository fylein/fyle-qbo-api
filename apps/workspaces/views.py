import logging

from django.contrib.auth import get_user_model
from django.db import connection
from django_q.tasks import async_task
from fyle_rest_auth.utils import AuthUtils
from qbosdk import exceptions as qbo_exc
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import status
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from apps.exceptions import handle_view_exceptions
from apps.workspaces.actions import (
    connect_qbo_oauth,
    delete_qbo_refresh_token,
    export_to_qbo,
    get_workspace_admin,
    setup_e2e_tests,
    update_or_create_workspace,
)
from apps.workspaces.models import LastExportDetail, QBOCredential, Workspace, WorkspaceGeneralSettings
from apps.workspaces.permissions import IsAuthenticatedForInternalAPI
from apps.workspaces.serializers import (
    LastExportDetailSerializer,
    QBOCredentialSerializer,
    WorkSpaceGeneralSettingsSerializer,
    WorkspaceSerializer,
)
from apps.quickbooks_online.utils import QBOConnector
from fyle_qbo_api.utils import invalidate_qbo_credentials
from apps.workspaces.utils import generate_qbo_refresh_token

logger = logging.getLogger(__name__)
logger.level = logging.INFO

User = get_user_model()
auth_utils = AuthUtils()


class TokenHealthView(generics.RetrieveAPIView):
    """
    Token Health View
    """

    def get(self, request, *args, **kwargs):
        status_code = status.HTTP_200_OK
        message = "Quickbooks Online connection is active"

        workspace_id = kwargs.get('workspace_id')
        qbo_credentials = QBOCredential.objects.filter(workspace=workspace_id).first()

        if not qbo_credentials:
            status_code = status.HTTP_400_BAD_REQUEST
            message = "Quickbooks Online credentials not found"
        elif qbo_credentials.is_expired:
            status_code = status.HTTP_400_BAD_REQUEST
            message = "Quickbooks Online connection expired"
        elif not qbo_credentials.refresh_token:
            status_code = status.HTTP_400_BAD_REQUEST
            message = "Quickbooks Online disconnected"
        else:
            try:
                qbo_connector = QBOConnector(qbo_credentials, workspace_id=workspace_id)
                qbo_connector.get_company_preference()
            except (qbo_exc.WrongParamsError, qbo_exc.InvalidTokenError):
                invalidate_qbo_credentials(workspace_id, qbo_credentials)
                status_code = status.HTTP_400_BAD_REQUEST
                message = "Quickbooks Online connection expired"

        return Response({"message": message}, status=status_code)


class WorkspaceView(generics.CreateAPIView, generics.RetrieveUpdateAPIView):
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
        workspace = update_or_create_workspace(user, access_token)

        return Response(data=WorkspaceSerializer(workspace).data, status=status.HTTP_200_OK)

    def get(self, request):
        """
        Get workspace
        """
        user = User.objects.get(user_id=request.user)
        org_id = request.query_params.get('org_id')
        workspaces = Workspace.objects.filter(user__in=[user], fyle_org_id=org_id).all()
        logger.info('User id %s', request.user)
        if workspaces:
            logger.info('Workspace detail %s', workspaces)
            async_task(
                "apps.workspaces.tasks.async_update_workspace_name",
                workspaces[0],
                request.META.get("HTTP_AUTHORIZATION"),
                q_options={'cluster': 'import'}
            )
        else:
            logger.info('No workspace found for user %s with org_id %s', request.user, org_id)

        return Response(data=WorkspaceSerializer(workspaces, many=True).data, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs):
        """
        PATCH workspace
        """
        workspace_instance = Workspace.objects.get(pk=kwargs['workspace_id'])
        serializer = WorkspaceSerializer(workspace_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)


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

        return Response(data={'message': 'Ready'}, status=status.HTTP_200_OK)


class ConnectQBOView(generics.CreateAPIView, generics.RetrieveUpdateAPIView):
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
            logger.info('Invalid/Expired Authorization Code or QBO application not found - %s', {'error': e.response})
            return Response({'message': 'Invalid/Expired Authorization Code or QBO application not found'}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request, **kwargs):
        """Delete QBO refresh_token"""
        return delete_qbo_refresh_token(kwargs['workspace_id'])

    @handle_view_exceptions()
    def get(self, request, **kwargs):
        """
        Get QBO Credentials in Workspace
        """
        qbo_credentials = QBOCredential.objects.get(workspace=kwargs['workspace_id'])

        return Response(data=QBOCredentialSerializer(qbo_credentials).data, status=status.HTTP_200_OK if qbo_credentials.refresh_token and not qbo_credentials.is_expired else status.HTTP_400_BAD_REQUEST)


class GeneralSettingsView(generics.RetrieveAPIView):
    """
    General Settings
    """

    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'
    queryset = WorkspaceGeneralSettings.objects.all()
    serializer_class = WorkSpaceGeneralSettingsSerializer


class ExportToQBOView(generics.CreateAPIView):
    """
    Export Expenses to QBO
    """

    def post(self, request, *args, **kwargs):
        export_to_qbo(workspace_id=kwargs['workspace_id'], triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC)

        return Response(status=status.HTTP_200_OK)


class LastExportDetailView(generics.RetrieveAPIView):
    """
    Last Export Details
    """

    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'

    queryset = LastExportDetail.objects.filter(last_exported_at__isnull=False, total_expense_groups_count__gt=0)
    serializer_class = LastExportDetailSerializer


class WorkspaceAdminsView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        """
        Get Admins for the workspaces
        """
        admin_email = get_workspace_admin(kwargs['workspace_id'])

        return Response(data=admin_email, status=status.HTTP_200_OK)


class SetupE2ETestView(generics.CreateAPIView):
    """
    QBO Workspace
    """

    authentication_classes = []
    permission_classes = [IsAuthenticatedForInternalAPI]

    def post(self, request, **kwargs):
        """
        Setup end to end test for a given workspace
        """
        return setup_e2e_tests(kwargs['workspace_id'], connection)
