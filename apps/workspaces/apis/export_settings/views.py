from rest_framework import generics, mixins
from rest_framework.response import Response

from apps.workspaces.models import WorkspaceGeneralSettings, Workspace
from apps.mappings.models import GeneralMapping
from apps.workspaces.serializers import WorkspaceSerializer

from .serializers import ExportSettingsReadSerializer, GeneralMappingsSerializer

class ExportSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = ExportSettingsReadSerializer
    authentication_classes = []
    permission_classes = []
    lookup_field = 'workspace_id'

    def get_object(self):
        return Workspace.objects.filter(id=self.kwargs['workspace_id']).first()