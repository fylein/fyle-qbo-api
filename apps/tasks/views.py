from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from django.db.models import Q
from fyle_qbo_api.utils import assert_valid

from .models import TaskLog
from .serializers import TaskLogSerializer


class TasksView(generics.ListAPIView):
    """
    Tasks view
    """
    serializer_class = TaskLogSerializer

    def get_queryset(self):
        """
        Return task logs in workspace
        """
        task_status = self.request.query_params.getlist('status')
        expense_group_ids = self.request.query_params.get('expense_group_ids')

        if len(task_status) == 1 and task_status[0] == 'IN_PROGRESS' and expense_group_ids:
            expense_group_ids = expense_group_ids.split(',')
            filters = {
                'workspace_id':self.kwargs['workspace_id'],
                'type__in':['CREATE_BILL','CREATE_CHECK','CREATING_CREDIT_CARD_PURCHASE','CREATING_JOURNAL_ENTRY'],
                'expense_group__in':expense_group_ids
            }
        else:
            filters = {
                'workspace_id':self.kwargs['workspace_id'],
                'status__in':task_status,
            }

        return TaskLog.objects.filter(**filters).order_by('-updated_at').all()


class TasksByIdView(generics.RetrieveAPIView):
    """
    Get Task by Ids
    """
    serializer_class = TaskLogSerializer

    def get(self, request, *args, **kwargs):
        """
        Get task logs by ids
        """
        task_log_ids = self.request.query_params.getlist('id', [])

        assert_valid(task_log_ids != [], 'task log ids not found')

        task_logs = TaskLog.objects.filter(id__in=task_log_ids).all()

        return Response(
            data=self.serializer_class(task_logs, many=True).data,
            status=status.HTTP_200_OK
        )


class TasksByExpenseGroupIdView(generics.RetrieveAPIView):
    """
    Get Task by Ids
    """
    serializer_class = TaskLogSerializer

    def get(self, request, *args, **kwargs):
        """
        Get task logs by ids
        """
        task_logs = TaskLog.objects.filter(expense_group_id=kwargs['expense_group_id']).all()

        return Response(
            data=self.serializer_class(task_logs, many=True).data,
            status=status.HTTP_200_OK
        )
