from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from apps.tasks.models import TaskLog
from apps.tasks.serializers import TaskLogSerializer
from fyle_qbo_api.utils import LookupFieldMixin


class TasksView(LookupFieldMixin, generics.ListAPIView):
    """
    Tasks view
    """

    queryset = TaskLog.objects.all()
    serializer_class = TaskLogSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {'type': {'exact', 'in'}, 'expense_group_id': {'exact', 'in'}, 'status': {'exact', 'in'}}
    ordering_fields = ('updated_at',)
