from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import generics

from fyle_qbo_api.utils import assert_valid

from apps.fyle.models import ExpenseGroup
from apps.tasks.models import TaskLog
from apps.workspaces.models import QBOCredential

from .utils import QBOConnector
from .tasks import create_bill, schedule_bills_creation, create_check, schedule_checks_creation, \
    create_credit_card_purchase, schedule_credit_card_purchase_creation, create_journal_entry,\
    schedule_journal_entry_creation
from .models import Bill, Cheque, CreditCardPurchase, JournalEntry
from .serializers import BillSerializer, CheckSerializer, CreditCardPurchaseSerializer, JournalEntrySerializer


class VendorView(viewsets.ViewSet):
    """
    Vendor view
    """

    def get_vendors(self, request, **kwargs):
        """
        Get vendors from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(
                workspace_id=kwargs['workspace_id'])

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


class EmployeeView(viewsets.ViewSet):
    """
    Employee view
    """

    def get_employees(self, request, **kwargs):
        """
        Get employees from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(
                workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials)

            employees = qbo_connector.get_employees()

            return Response(
                data=employees,
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
            qbo_credentials = QBOCredential.objects.get(
                workspace_id=kwargs['workspace_id'])

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
            qbo_credentials = QBOCredential.objects.get(
                workspace_id=kwargs['workspace_id'])

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
            qbo_credentials = QBOCredential.objects.get(
                workspace_id=kwargs['workspace_id'])

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


class CustomerView(viewsets.ViewSet):
    """
    Department view
    """

    def get_customers(self, request, **kwargs):
        """
        Get departments from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(
                workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials)

            customers = qbo_connector.get_customers()

            return Response(
                data=customers,
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
        return Bill.objects.filter(expense_group__workspace_id=self.kwargs['workspace_id']).order_by('-updated_at')

    def post(self, request, *args, **kwargs):
        """
        Create bill from expense group
        """
        expense_group_id = request.data.get('expense_group_id')
        task_log_id = request.data.get('task_log_id')

        assert_valid(expense_group_id is not None, 'expense group id not found')
        assert_valid(task_log_id is not None, 'Task Log id not found')

        expense_group = ExpenseGroup.objects.get(pk=expense_group_id)
        task_log = TaskLog.objects.get(pk=task_log_id)

        create_bill(expense_group, task_log)

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class BillScheduleView(generics.CreateAPIView):
    """
    Schedule bills create
    """

    def post(self, request, *args, **kwargs):
        expense_group_ids = request.data.get('expense_group_ids', [])

        schedule_bills_creation(
            kwargs['workspace_id'], expense_group_ids, request.user)

        return Response(
            status=status.HTTP_200_OK
        )


class CheckView(generics.ListCreateAPIView):
    """
    Create Check
    """
    serializer_class = CheckSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return Cheque.objects.filter(expense_group__workspace_id=self.kwargs['workspace_id']).order_by(
            '-updated_at'
        )

    def post(self, request, *args, **kwargs):
        """
        Create check from expense group
        """
        expense_group_id = request.data.get('expense_group_id')
        task_log_id = request.data.get('task_log_id')

        assert_valid(expense_group_id is not None, 'expense group id not found')
        assert_valid(task_log_id is not None, 'Task Log id not found')

        expense_group = ExpenseGroup.objects.get(pk=expense_group_id)
        task_log = TaskLog.objects.get(pk=task_log_id)

        create_check(expense_group, task_log)

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class CheckScheduleView(generics.CreateAPIView):
    """
    Schedule checks creation
    """

    def post(self, request, *args, **kwargs):
        expense_group_ids = request.data.get('expense_group_ids', [])

        schedule_checks_creation(
            kwargs['workspace_id'], expense_group_ids, request.user)

        return Response(
            status=status.HTTP_200_OK
        )


class CreditCardPurchaseView(generics.ListCreateAPIView):
    """
    Create CreditCardPurchase
    """
    serializer_class = CreditCardPurchaseSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return CreditCardPurchase.objects.filter(
            expense_group__workspace_id=self.kwargs['workspace_id']
        ).order_by('-updated_at')

    def post(self, request, *args, **kwargs):
        """
        Create credit_card_purchase from expense group
        """
        expense_group_id = request.data.get('expense_group_id')
        task_log_id = request.data.get('task_log_id')

        assert_valid(expense_group_id is not None, 'Expense ids not found')
        assert_valid(task_log_id is not None, 'Task Log id not found')

        expense_group = ExpenseGroup.objects.get(pk=expense_group_id)
        task_log = TaskLog.objects.get(pk=task_log_id)

        create_credit_card_purchase(expense_group, task_log)

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class CreditCardPurchaseScheduleView(generics.CreateAPIView):
    """
    Schedule credit_card_purchase create
    """

    def post(self, request, *args, **kwargs):
        expense_group_ids = request.data.get('expense_group_ids', [])

        schedule_credit_card_purchase_creation(
            kwargs['workspace_id'], expense_group_ids, request.user)

        return Response(
            status=status.HTTP_200_OK
        )


class JournalEntryView(generics.ListCreateAPIView):
    """
    Create JournalEntry
    """
    serializer_class = JournalEntrySerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return JournalEntry.objects.filter(
            expense_group__workspace_id=self.kwargs['workspace_id']
        ).order_by('-updated_at')

    def post(self, request, *args, **kwargs):
        """
        Create JournalEntry from expense group
        """
        expense_group_id = request.data.get('expense_group_id')
        task_log_id = request.data.get('task_log_id')

        assert_valid(expense_group_id is not None, 'Expense ids not found')
        assert_valid(task_log_id is not None, 'Task Log id not found')

        expense_group = ExpenseGroup.objects.get(pk=expense_group_id)
        task_log = TaskLog.objects.get(pk=task_log_id)

        create_journal_entry(expense_group, task_log)

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class JournalEntryScheduleView(generics.CreateAPIView):
    """
    Schedule JournalEntry creation
    """

    def post(self, request, *args, **kwargs):
        expense_group_ids = request.data.get('expense_group_ids', [])

        schedule_journal_entry_creation(
            kwargs['workspace_id'], expense_group_ids, request.user)

        return Response(
            status=status.HTTP_200_OK
        )
