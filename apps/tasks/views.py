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
        
        expense_group_ids = self.request.query_params.get('ids')

        if len(task_status) == 1 and task_status[0] == 'ALL' and expense_group_ids:
            expense_group_ids = expense_group_ids.split(',')
            return TaskLog.objects.filter(
                ~Q(type__in=['FETCHING_EXPENSES' ,'CREATING_VENDOR_PAYMENT']),
                workspace_id=self.kwargs['workspace_id'],
                status='IN_PROGRESS',
                expense_group__in=expense_group_ids
            ).order_by('-updated_at').all()

        print(task_status)    
        return TaskLog.objects.filter(workspace_id=self.kwargs['workspace_id'],
                                           status__in=task_status).order_by('-updated_at').all()


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
