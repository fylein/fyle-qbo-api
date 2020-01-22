from rest_framework.views import status
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response

from django_q.tasks import async_task

from apps.workspaces.models import FyleCredential
from apps.tasks.models import TaskLog
from apps.tasks.serializers import TaskLogSerializer

from .tasks import create_expense_groups
from .utils import FyleConnector
from .models import Expense, ExpenseGroup
from .serializers import ExpenseGroupSerializer, ExpenseSerializer


class ExpenseGroupView(generics.ListCreateAPIView):
    """
    List Fyle Expenses
    """
    serializer_class = ExpenseGroupSerializer

    def get_queryset(self):
        return ExpenseGroup.objects.filter(workspace_id=self.kwargs['workspace_id'])

    def post(self, request, *args, **kwargs):
        """
        Create expense groups
        """
        export_non_reimbursable = request.data.get('export_non_reimbursable', False)
        state = request.data.get('state', ['PAYMENT_PROCESSING'])

        task_log = TaskLog.objects.create(
            workspace_id=self.kwargs['workspace_id'],
            type='FETCHING_EXPENSES',
            status='IN_PROGRESS'
        )
        task_id = async_task(create_expense_groups, kwargs['workspace_id'], state, export_non_reimbursable, task_log)

        task_log.task_id = task_id
        task_log.detail = {
            'message': 'Creating expense groups'
        }
        task_log.save(update_fields=['task_id', 'detail'])

        return Response(
            data=TaskLogSerializer(task_log).data,
            status=status.HTTP_200_OK
        )


class ExpenseView(generics.RetrieveAPIView):
    """
    Expense view
    """
    def get(self, request, *args, **kwargs):
        """
        Get expenses
        """
        try:
            expense_group = ExpenseGroup.objects.get(
                workspace_id=kwargs['workspace_id'], pk=kwargs['expense_group_id']
            )
            expenses = Expense.objects.filter(id__in=expense_group.expenses.values_list('id', flat=True))
            return Response(
                data=ExpenseSerializer(expenses, many=True).data,
                status=status.HTTP_200_OK
            )

        except ExpenseGroup.DoesNotExist:
            return Response(
                data={
                    'message': 'Expense group not found'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class EmployeeView(viewsets.ViewSet):
    """
    Employee view
    """
    def get_employees(self, request, **kwargs):
        """
        Get employees from Fyle
        """
        try:
            fyle_credentials = FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])

            fyle_connector = FyleConnector(fyle_credentials.refresh_token)

            employees = fyle_connector.get_employees()

            return Response(
                data=employees,
                status=status.HTTP_200_OK
            )
        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Fyle credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoryView(viewsets.ViewSet):
    """
    Category view
    """
    def get_categories(self, request, **kwargs):
        """
        Get categories from Fyle
        """
        try:
            active_only = request.GET.get('active_only', False)
            fyle_credentials = FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])

            fyle_connector = FyleConnector(fyle_credentials.refresh_token)

            categories = fyle_connector.get_categories(active_only=active_only)

            return Response(
                data=categories,
                status=status.HTTP_200_OK
            )
        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Fyle credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class CostCenterView(viewsets.ViewSet):
    """
    Cost center view
    """
    def get_cost_centers(self, request, **kwargs):
        """
        Get cost centers from Fyle
        """
        try:
            active_only = request.GET.get('active_only', False)
            fyle_credentials = FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])

            fyle_connector = FyleConnector(fyle_credentials.refresh_token)

            cost_centers = fyle_connector.get_cost_centers(active_only=active_only)

            return Response(
                data=cost_centers,
                status=status.HTTP_200_OK
            )
        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Fyle credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ProjectView(viewsets.ViewSet):
    """
    Project view
    """
    def get_projects(self, request, **kwargs):
        """
        Get projects from Fyle
        """
        try:
            active_only = request.GET.get('active_only', False)
            fyle_credentials = FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])

            fyle_connector = FyleConnector(fyle_credentials.refresh_token)

            projects = fyle_connector.get_projects(active_only=active_only)

            return Response(
                data=projects,
                status=status.HTTP_200_OK
            )
        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Fyle credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
