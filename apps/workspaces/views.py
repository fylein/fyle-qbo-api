import json

from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from fylesdk import exceptions as fyle_exc
from qbosdk import exceptions as qbo_exc


from fyle_rest_auth.utils import AuthUtils
from fyle_rest_auth.models import AuthToken
from fyle_rest_auth.helpers import get_fyle_admin

from fyle_qbo_api.utils import assert_valid

from apps.quickbooks_online.utils import QBOConnector
from apps.fyle.utils import FyleConnector
from apps.fyle.helpers import get_cluster_domain

from .models import Workspace, FyleCredential, QBOCredential, WorkspaceGeneralSettings, WorkspaceSchedule
from .utils import generate_qbo_refresh_token, create_or_update_general_settings
from .tasks import schedule_sync, run_sync_schedule
from .serializers import WorkspaceSerializer, FyleCredentialSerializer, QBOCredentialSerializer, \
    WorkSpaceGeneralSettingsSerializer, WorkspaceScheduleSerializer
from ..fyle.models import ExpenseGroupSettings

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

        workspace = Workspace.objects.filter(fyle_org_id=org_id).first()

        if workspace:
            workspace.user.add(User.objects.get(user_id=request.user))
            cache.delete(str(workspace.id))
        else:
            workspace = Workspace.objects.create(name=org_name, fyle_org_id=org_id)

            ExpenseGroupSettings.objects.create(workspace_id=workspace.id)

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

            tokens = auth_utils.generate_fyle_refresh_token(authorization_code)
            refresh_token = tokens['refresh_token']

            fyle_user = get_fyle_admin(tokens['access_token'], None)
            org_name = fyle_user['data']['org']['name']
            org_id = fyle_user['data']['org']['id']

            assert_valid(workspace.fyle_org_id and workspace.fyle_org_id == org_id,
                         'Please select the correct Fyle account - {0}'.format(workspace.name))

            workspace.name = org_name
            workspace.fyle_org_id = org_id
            workspace.save()

            cluster_domain = get_cluster_domain(refresh_token)

            fyle_credentials, _ = FyleCredential.objects.update_or_create(
                workspace_id=kwargs['workspace_id'],
                defaults={
                    'refresh_token': refresh_token,
                    'cluster_domain': cluster_domain
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

                try:
                    qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

                    company_info = qbo_connector.get_company_info()
                    qbo_credentials.country = company_info['Country']
                    qbo_credentials.company_name = company_info['CompanyName']
                    qbo_credentials.save()

                except WrongParamsError as exception:
                    logger.error(exception.response)

                workspace.qbo_realm_id = realm_id
                workspace.save()
            else:
                assert_valid(realm_id == qbo_credentials.realm_id,
                             'Please choose the correct Quickbooks online account')
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

    def patch(self, request, **kwargs):
        """Delete QBO refresh_token"""
        workspace_id = kwargs['workspace_id']
        qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
        qbo_credentials.refresh_token = None
        qbo_credentials.save()

        return Response(data={
            'workspace_id': workspace_id,
            'message': 'QBO Refresh Token deleted'
        })

    def get(self, request, **kwargs):
        """
        Get QBO Credentials in Workspace
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace=kwargs['workspace_id'], refresh_token__isnull=False)
            # qbo_credentials.objects.get(refreshtoken__isnull=False)

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
        run_sync_schedule(kwargs['workspace_id'])
        return Response(
            status=status.HTTP_200_OK
        )


class ScheduleView(viewsets.ViewSet):
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


        workspace_schedule_settings = schedule_sync(
            workspace_id=kwargs['workspace_id'],
            schedule_enabled=schedule_enabled,
            hours=hours
        )

        return Response(
            data=WorkspaceScheduleSerializer(workspace_schedule_settings).data,
            status=status.HTTP_200_OK
        )

    def get(self, *args, **kwargs):
        try:
            workspace_schedule = WorkspaceSchedule.objects.get(workspace_id=kwargs['workspace_id'])

            return Response(
                data=WorkspaceScheduleSerializer(workspace_schedule).data,
                status=status.HTTP_200_OK
            )
        except WorkspaceSchedule.DoesNotExist:
            return Response(
                data={
                    'message': 'Workspace schedule does not exist in workspace'
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
