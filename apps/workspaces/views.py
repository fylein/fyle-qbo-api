import json

from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from fylesdk import exceptions as fyle_exc
from qbosdk import exceptions as qbo_exc


from fyle_rest_auth.utils import AuthUtils
from fyle_rest_auth.models import AuthToken

from fyle_qbo_api.utils import assert_valid

from .models import Workspace, FyleCredential, QBOCredential, WorkspaceSettings, WorkspaceGeneralSettings
from .utils import generate_qbo_refresh_token, create_or_update_general_settings
from .tasks import schedule_sync, run_sync_schedule
from .serializers import WorkspaceSerializer, FyleCredentialSerializer, QBOCredentialSerializer, \
    WorkspaceSettingsSerializer, WorkSpaceGeneralSettingsSerializer

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

        auth_tokens = AuthToken.objects.get(user__user_id=request.user)
        fyle_user = auth_utils.get_fyle_user(auth_tokens.refresh_token)
        org_name = fyle_user['org_name']
        org_id = fyle_user['org_id']

        workspace = Workspace.objects.filter(fyle_org_id=org_id).first()

        if workspace:
            workspace.user.add(User.objects.get(user_id=request.user))
        else:
            workspace = Workspace.objects.create(name=org_name, fyle_org_id=org_id)

            workspace.user.add(User.objects.get(user_id=request.user))

            FyleCredential.objects.update_or_create(
                refresh_token=auth_tokens.refresh_token,
                workspace_id=workspace.id
            )

        return Response(
            data=WorkspaceSerializer(workspace).data,
            status=status.HTTP_200_OK
        )

    def get_all(self, request):
        """
        Get all workspaces
        """
        user = User.objects.get(user_id=request.user)
        workspaces = Workspace.objects.filter(user__in=[user]).all()

        return Response(
            data=WorkspaceSerializer(workspaces, many=True).data,
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

        Workspace.objects.raw('Select 1 from workspaces_workspace')

        return Response(
            data={
                'message': 'Ready'
            },
            status=status.HTTP_200_OK
        )


class ConnectFyleView(viewsets.ViewSet):
    """
    Fyle Connect Oauth View
    """
    def post(self, request, **kwargs):
        """
        Post of QBO Credentials
        """
        try:
            authorization_code = request.data.get('code')

            workspace = Workspace.objects.get(id=kwargs['workspace_id'])

            refresh_token = auth_utils.generate_fyle_refresh_token(authorization_code)['refresh_token']
            fyle_user = auth_utils.get_fyle_user(refresh_token)
            org_id = fyle_user['org_id']
            org_name = fyle_user['org_name']

            assert_valid(workspace.fyle_org_id and workspace.fyle_org_id == org_id,
                         'Please select the correct Fyle account - {0}'.format(workspace.name))

            workspace.name = org_name
            workspace.fyle_org_id = org_id
            workspace.save(update_fields=['name', 'fyle_org_id'])

            fyle_credentials, _ = FyleCredential.objects.update_or_create(
                workspace_id=kwargs['workspace_id'],
                defaults={
                    'refresh_token': refresh_token,
                }
            )

            return Response(
                data=FyleCredentialSerializer(fyle_credentials).data,
                status=status.HTTP_200_OK
            )
        except fyle_exc.UnauthorizedClientError:
            return Response(
                {
                    'message': 'Invalid Authorization Code'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        except fyle_exc.NotFoundClientError:
            return Response(
                {
                    'message': 'Fyle Application not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except fyle_exc.WrongParamsError:
            return Response(
                {
                    'message': 'Some of the parameters are wrong'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except fyle_exc.InternalServerError:
            return Response(
                {
                    'message': 'Wrong/Expired Authorization code'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    def delete(self, request, **kwargs):
        """Delete credentials"""
        workspace_id = kwargs['workspace_id']
        FyleCredential.objects.filter(workspace_id=workspace_id).delete()

        return Response(data={
            'workspace_id': workspace_id,
            'message': 'Fyle credentials deleted'
        })

    def get(self, request, **kwargs):
        """
        Get Fyle Credentials in Workspace
        """
        try:
            workspace = Workspace.objects.get(pk=kwargs['workspace_id'])
            fyle_credentials = FyleCredential.objects.get(workspace=workspace)

            if fyle_credentials:
                return Response(
                    data=FyleCredentialSerializer(fyle_credentials).data,
                    status=status.HTTP_200_OK
                )
        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Fyle Credentials not found in this workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ConnectQBOView(viewsets.ViewSet):
    """
    QBO Connect Oauth View
    """
    def post(self, request, **kwargs):
        """
        Post of QBO Credentials
        """
        try:
            authorization_code = request.data.get('code')
            realm_id = request.data.get('realm_id')

            refresh_token = generate_qbo_refresh_token(authorization_code)

            workspace = Workspace.objects.get(pk=kwargs['workspace_id'])

            qbo_credentials = QBOCredential.objects.filter(workspace=workspace).first()

            if not qbo_credentials:
                if workspace.qbo_realm_id:
                    assert_valid(realm_id == workspace.qbo_realm_id,
                                 'Please choose the correct Quickbooks online account')
                qbo_credentials = QBOCredential.objects.create(
                    refresh_token=refresh_token,
                    realm_id=realm_id,
                    workspace=workspace
                )
                workspace.qbo_realm_id = realm_id
                workspace.save(update_fields=['qbo_realm_id'])
            else:
                assert_valid(realm_id == qbo_credentials.realm_id,
                             'Please choose the correct aaaaa Quickbooks online account')
                qbo_credentials.refresh_token = refresh_token
                qbo_credentials.save()

            return Response(
                data=QBOCredentialSerializer(qbo_credentials).data,
                status=status.HTTP_200_OK
            )
        except qbo_exc.UnauthorizedClientError:
            return Response(
                {
                    'message': 'Invalid Authorization Code'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        except qbo_exc.NotFoundClientError:
            return Response(
                {
                    'message': 'QBO Application not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except qbo_exc.WrongParamsError as e:
            return Response(
                json.loads(e.response),
                status=status.HTTP_400_BAD_REQUEST
            )
        except qbo_exc.InternalServerError:
            return Response(
                {
                    'message': 'Wrong/Expired Authorization code'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    def delete(self, request, **kwargs):
        """Delete credentials"""
        workspace_id = kwargs['workspace_id']
        QBOCredential.objects.filter(workspace_id=workspace_id).delete()

        return Response(data={
            'workspace_id': workspace_id,
            'message': 'QBO credentials deleted'
        })

    def get(self, request, **kwargs):
        """
        Get QBO Credentials in Workspace
        """
        try:
            workspace = Workspace.objects.get(pk=kwargs['workspace_id'])
            qbo_credentials = QBOCredential.objects.get(workspace=workspace)

            return Response(
                data=QBOCredentialSerializer(qbo_credentials).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO Credentials not found in this workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ScheduledSyncView(viewsets.ViewSet):
    """
    Scheduled Sync
    """
    def post(self, request, **kwargs):
        """
        Scheduled sync
        """
        run_sync_schedule(kwargs['workspace_id'], request.user)
        return Response(
            status=status.HTTP_200_OK
        )


class SettingsView(viewsets.ViewSet):
    """
    Settings View
    """
    def post(self, request, **kwargs):
        """
        Post Settings
        """
        schedule_enabled = request.data.get('schedule_enabled')
        assert_valid(schedule_enabled is not None, 'Schedule enabled cannot be null')

        hours = request.data.get('hours')
        assert_valid(hours is not None, 'Hours cannot be left empty')

        next_run = request.data.get('next_run')
        assert_valid(next_run is not None, 'next_run value cannot be empty')

        settings = schedule_sync(
            workspace_id=kwargs['workspace_id'],
            schedule_enabled=schedule_enabled,
            hours=hours,
            next_run=next_run,
            user=request.user
        )

        return Response(
            data=WorkspaceSettingsSerializer(settings).data,
            status=status.HTTP_200_OK
        )

    def get(self, *args, **kwargs):
        try:
            qbo_credentials = WorkspaceSettings.objects.get(workspace_id=kwargs['workspace_id'])

            return Response(
                data=WorkspaceSettingsSerializer(qbo_credentials).data,
                status=status.HTTP_200_OK
            )
        except WorkspaceSettings.DoesNotExist:
            return Response(
                data={
                    'message': 'Workspace setting does not exist in workspace'
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
