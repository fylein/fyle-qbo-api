from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import generics

from django_q.tasks import async_task

from fyle_qbo_api.utils import assert_valid

from apps.workspaces.models import QBOCredential
from apps.fyle.models import ExpenseGroup
from apps.tasks.models import TaskLog
from apps.tasks.serializers import TaskLogSerializer

from .utils import QBOConnector
from .tasks import create_bill
from .models import Bill
from .serializers import BillSerializer


class VendorView(viewsets.ViewSet):
    """
    Vendor view
    """
    def get_vendors(self, request, **kwargs):
        """
        Get vendors from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials)

            vendors = qbo_connector.get_vendors()

            return Response(
                data=vendors,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class AccountView(viewsets.ViewSet):
    """
    Account view
    """
    def get_accounts(self, request, **kwargs):
        """
        Get accounts from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials)

            accounts = qbo_connector.get_accounts()

            return Response(
                data=accounts,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ClassView(viewsets.ViewSet):
    """
    Class view
    """
    def get_classes(self, request, **kwargs):
        """
        Get classes from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials)

            classes = qbo_connector.get_classes()

            return Response(
                data=classes,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class DepartmentView(viewsets.ViewSet):
    """
    Department view
    """
    def get_departments(self, request, **kwargs):
        """
        Get departments from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials)

            departments = qbo_connector.get_departments()

            return Response(
                data=departments,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class BillView(generics.ListCreateAPIView):
    """
    Create Bill
    """
    serializer_class = BillSerializer

    def get_queryset(self):
        return Bill.objects.filter(expense_group__workspace_id=self.kwargs['workspace_id'])

    def post(self, request, *args, **kwargs):
        """
        Create bill from expense group
        """
        expense_group_ids = request.data.get('expense_group_ids', [])

        assert_valid(expense_group_ids != [], 'Expense ids not found')

        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=kwargs['workspace_id'], id__in=expense_group_ids, bill__id__isnull=True
        ).all()

        task_logs = []

        completed_expense_groups = ExpenseGroup.objects.filter(
            workspace_id=kwargs['workspace_id'], id__in=expense_group_ids, bill__id__isnull=False
        ).all()

        for expense_group in completed_expense_groups:
            task_log = TaskLog.objects.get(expense_group=expense_group)
            task_logs.append(task_log)

        for expense_group in expense_groups:
            task_log, _ = TaskLog.objects.update_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={
                    'status': 'IN_PROGRESS',
                    'type': 'CREATING_BILL'
                }
            )
            task_id = async_task(create_bill, expense_group, task_log)

            detail = {
                'message': 'Creating bill for expense group {0}'.format(expense_group.id)
            }
            task_log.detail = detail
            task_log.task_id = task_id
            task_log.save(update_fields=['task_id', 'detail'])

            task_logs.append(task_log)

        return Response(
            data=TaskLogSerializer(task_logs, many=True).data,
            status=status.HTTP_200_OK
        )
