from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from django_filters.rest_framework import DjangoFilterBackend

from fyle_qbo_api.utils import LookupFieldMixin

from .models import TaskLog
from .serializers import TaskLogSerializer


class TasksView(LookupFieldMixin, generics.ListAPIView):
    """
    Tasks view
    """

    queryset = TaskLog.objects.all()
    serializer_class = TaskLogSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {
        'type': {'exact', 'in'},
        'expense_group_id': {'exact', 'in'},
        'status': {'exact', 'in'},
    }
    ordering_fields = ('updated_at',)
