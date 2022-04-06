from rest_framework import generics

from apps.tasks.models import Error

from .serializers import ErrorSerializer


class ErrorsView(generics.ListAPIView):
    serializer_class = ErrorSerializer
    authentication_classes = []
    permission_classes = []
    
    def get_queryset(self):
        return Error.objects.filter(workspace_id=self.kwargs['workspace_id'])
