import json

from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets

from fylesdk import exceptions as fyle_exc
from qbosdk import exceptions as qbo_exc

from fyle_rest_auth.utils import AuthUtils
from fyle_rest_auth.models import AuthToken

from .models import Workspace, FyleCredential, QBOCredential
from .utils import generate_qbo_refresh_token
from .serializers import WorkspaceSerializer, FyleCredentialSerializer, QBOCredentialSerializer


User = get_user_model()
auth_utils = AuthUtils()


class WorkspaceView(viewsets.ViewSet):
    """
    QBO Workspace
    """

    def post(self, request):
        """
        Create a Workspace
        """

        all_workspaces_count = Workspace.objects.filter(user__email=request.user).count()

        workspace = Workspace.objects.create(
            name='Workspace {0}'.format(all_workspaces_count + 1),
            user=User.objects.get(email=request.user)
        )

        if all_workspaces_count == 0:
            auth_tokens = AuthToken.objects.get(user__email=request.user)

            FyleCredential.objects.create(
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
        user = User.objects.get(email=request.user)
        workspaces = Workspace.objects.filter(user=user).all()

        return Response(
            data=WorkspaceSerializer(workspaces, many=True).data,
            status=status.HTTP_200_OK
        )

    def get_by_id(self, request, **kwargs):
        """
        Get Workspace by id
        """
        try:
            user = User.objects.get(email=request.user)
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

            refresh_token = auth_utils.generate_fyle_refresh_token(authorization_code)['refresh_token']

            fyle_credentials, _ = FyleCredential.objects.update_or_create(
                workspace_id=kwargs['workspace_id'],
                defaults={
                    'refresh_token': refresh_token
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
                status=status.HTTP_401_UNAUTHORIZED
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
                qbo_credentials = QBOCredential.objects.create(
                    refresh_token=refresh_token,
                    realm_id=realm_id,
                    workspace=workspace
                )
            else:
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
