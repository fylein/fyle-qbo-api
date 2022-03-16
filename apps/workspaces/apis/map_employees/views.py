from rest_framework import generics, mixins

from apps.workspaces.models import WorkspaceGeneralSettings

from .serializers import MapEmployeesSerializer


class MapEmployeesView(generics.CreateAPIView, mixins.RetrieveModelMixin):
    serializer_class = MapEmployeesSerializer
    authentication_classes = []
    permission_classes = []

    def get_object(self):
        return WorkspaceGeneralSettings.objects.filter(
            workspace_id=self.kwargs['workspace_id']
        ).first()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
