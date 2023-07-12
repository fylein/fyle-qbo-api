import logging
from django.conf import settings
from django.contrib.auth import get_user_model

from django.db import connection
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework.permissions import IsAuthenticated

from qbosdk import exceptions as qbo_exc

from fyle_rest_auth.utils import AuthUtils

from .models import Workspace, QBOCredential, WorkspaceGeneralSettings, LastExportDetail
from .utils import generate_qbo_refresh_token
from .tasks import export_to_qbo
from .serializers import (
    WorkspaceSerializer,
    QBOCredentialSerializer,
    WorkSpaceGeneralSettingsSerializer,
    LastExportDetailSerializer,
)
from .permissions import IsAuthenticatedForTest
from apps.exceptions import handle_view_exceptions

from .actions import (
    update_or_create_workspace,
    connect_qbo_oauth,
    get_workspace_admin,
    setup_e2e_tests,
    delete_qbo_refresh_token,
)

logger = logging.getLogger(__name__)
logger.level = logging.INFO

User = get_user_model()
auth_utils = AuthUtils()


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

        return Response(
            data=WorkspaceSerializer(workspace).data, status=status.HTTP_200_OK
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
            status=status.HTTP_200_OK,
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
        except (
            qbo_exc.UnauthorizedClientError,
            qbo_exc.NotFoundClientError,
            qbo_exc.WrongParamsError,
            qbo_exc.InternalServerError,
        ) as e:
            logger.info(
                'Invalid/Expired Authorization Code or QBO application not found - %s',
                {'error': e.response},
            )
            return Response(
                {
                    'message': 'Invalid/Expired Authorization Code or QBO application not found'
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def patch(self, request, **kwargs):
        """Delete QBO refresh_token"""
        return delete_qbo_refresh_token(kwargs['workspace_id'])

    @handle_view_exceptions()
    def get(self, request, **kwargs):
        """
        Get QBO Credentials in Workspace
        """
        qbo_credentials = QBOCredential.objects.get(
            workspace=kwargs['workspace_id'], is_expired=False
        )

        return Response(
            data=QBOCredentialSerializer(qbo_credentials).data,
            status=status.HTTP_200_OK
            if qbo_credentials.refresh_token
            else status.HTTP_400_BAD_REQUEST,
        )


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
        export_to_qbo(workspace_id=kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)


class LastExportDetailView(generics.RetrieveAPIView):
    """
    Last Export Details
    """

    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'

    queryset = LastExportDetail.objects.filter(
        last_exported_at__isnull=False, total_expense_groups_count__gt=0
    )
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
    permission_classes = [IsAuthenticatedForTest]

    def post(self, request, **kwargs):
        """
        Setup end to end test for a given workspace
        """
        return setup_e2e_tests(kwargs['workspace_id'], connection)
