from rest_framework import generics

from apps.tasks.models import Error

from .serializers import ErrorSerializer


class ErrorsView(generics.ListAPIView):
    serializer_class = ErrorSerializer
    
    def get_queryset(self):
        type = self.request.query_params.get('type')
        
        is_resolved = self.request.query_params.get('is_resolved')

        if is_resolved.lower() == 'true':
            is_resolved = True
        else:
            is_resolved = False

        params = {
            'is_resolved': is_resolved,
            'workspace__id': self.kwargs.get('workspace_id')
        }

        if type:
            params['type'] = type
        
        return Error.objects.filter(**params)
