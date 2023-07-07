from rest_framework import generics

from apps.workspaces.apis.advanced_configurations.serializers import (
    AdvancedConfigurationsSerializer,
)
from apps.workspaces.models import Workspace


class AdvancedConfigurationsView(generics.RetrieveUpdateAPIView):
    serializer_class = AdvancedConfigurationsSerializer

    def get_object(self):
        return Workspace.objects.filter(id=self.kwargs["workspace_id"]).first()
