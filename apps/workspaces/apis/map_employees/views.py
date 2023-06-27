from rest_framework import generics

from apps.workspaces.models import Workspace

from .serializers import MapEmployeesSerializer


class MapEmployeesView(generics.RetrieveUpdateAPIView):
    serializer_class = MapEmployeesSerializer

    def get_object(self):
        return Workspace.objects.filter(id=self.kwargs["workspace_id"]).first()
