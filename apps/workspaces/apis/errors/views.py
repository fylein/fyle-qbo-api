from rest_framework import generics

from apps.tasks.models import Error

from .serializers import ErrorSerializer


class ErrorsView(generics.ListAPIView):
    serializer_class = ErrorSerializer
    authentication_classes = []
    permission_classes = []
    
    def get_queryset(self):
        type = self.request.query_params.get('type')
        params = {
            'is_resolved': self.request.query_params.get('is_resolved', False),
            'workspace__id': self.kwargs.get('workspace_id')
        }
        if type:
            params['type'] = type
        
        return Error.objects.filter(**params)
