from rest_framework import generics, status
from rest_framework.response import Response
from apps.workspaces.apis.import_settings.serializers import ImportSettingsSerializer
from apps.workspaces.models import Workspace
from fyle_integrations_imports.models import ImportLog


class ImportSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = ImportSettingsSerializer

    def get_object(self):
        return Workspace.objects.filter(id=self.kwargs['workspace_id']).first()


class ImportCodeFieldView(generics.GenericAPIView):
    """
    Import Code Field View
    """
    def get(self, request, *args, **kwargs):
        workspace_id = kwargs['workspace_id']
        category_import_log = ImportLog.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').first()

        response_data = {
            'ACCOUNT': False if category_import_log else True,
        }

        return Response(
            data=response_data,
            status=status.HTTP_200_OK
        )
