from rest_framework import generics

from apps.workspaces.models import Workspace

from .serializers import AdvancedConfigurationsSerializer


class AdvancedConfigurationsView(generics.RetrieveUpdateAPIView):
    serializer_class = AdvancedConfigurationsSerializer

    def get_object(self):
        return Workspace.objects.filter(id=self.kwargs['workspace_id']).first()
