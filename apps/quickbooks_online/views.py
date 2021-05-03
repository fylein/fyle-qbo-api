from django.db.models import Q
from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import generics

from qbosdk.exceptions import WrongParamsError

from fyle_accounting_mappings.models import DestinationAttribute, MappingSetting
from fyle_accounting_mappings.serializers import DestinationAttributeSerializer

from fyle_qbo_api.utils import assert_valid

from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.tasks.models import TaskLog
from apps.workspaces.models import QBOCredential, WorkspaceGeneralSettings, Workspace
from apps.fyle.serializers import ExpenseGroupSettingsSerializer

from .utils import QBOConnector
from .tasks import create_bill, schedule_bills_creation, create_cheque, schedule_cheques_creation, \
    create_credit_card_purchase, schedule_credit_card_purchase_creation, create_journal_entry, \
    schedule_journal_entry_creation, create_bill_payment, process_reimbursements, check_qbo_object_status
from .models import Bill, Cheque, CreditCardPurchase, JournalEntry
from .serializers import BillSerializer, ChequeSerializer, CreditCardPurchaseSerializer, JournalEntrySerializer, \
    QuickbooksFieldSerializer


class VendorView(generics.ListCreateAPIView):
    """
    Vendor view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='VENDOR', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get vendors from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            vendors = qbo_connector.sync_vendors()

            return Response(
                data=self.serializer_class(vendors, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class EmployeeView(generics.ListCreateAPIView):
    """
    Employee view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='EMPLOYEE', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get employees from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            employees = qbo_connector.sync_employees()

            return Response(
                data=self.serializer_class(employees, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class AccountView(generics.ListCreateAPIView):
    """
    Account view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='ACCOUNT', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get accounts from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            accounts = qbo_connector.sync_accounts(account_type='Expense')

            return Response(
                data=self.serializer_class(accounts, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class CreditCardAccountView(generics.ListCreateAPIView):
    """
    Account view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='CREDIT_CARD_ACCOUNT', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get accounts from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            accounts = qbo_connector.sync_accounts(account_type='Credit Card')

            return Response(
                data=self.serializer_class(accounts, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class BankAccountView(generics.ListCreateAPIView):
    """
    Account view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='BANK_ACCOUNT', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get accounts from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            accounts = qbo_connector.sync_accounts(account_type='Bank')

            return Response(
                data=self.serializer_class(accounts, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class AccountsPayableView(generics.ListCreateAPIView):
    """
    Account view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='ACCOUNTS_PAYABLE', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get accounts from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            accounts = qbo_connector.sync_accounts(account_type='Accounts Payable')

            return Response(
                data=self.serializer_class(accounts, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class BillPaymentAccountView(generics.ListCreateAPIView):
    """
    BillPaymentAccount view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='BANK_ACCOUNT', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get bill payment accounts from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            accounts = qbo_connector.sync_accounts(account_type='Bank')

            return Response(
                data=self.serializer_class(accounts, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ClassView(generics.ListCreateAPIView):
    """
    Class view
    """

    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='CLASS', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get classes from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            classes = qbo_connector.sync_classes()

            return Response(
                data=self.serializer_class(classes, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class PreferencesView(generics.RetrieveAPIView):
    """
    Preferences View
    """
    def get(self, request, *args, **kwargs):
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            preferences = qbo_connector.get_company_preference()

            return Response(
                data=preferences,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except WrongParamsError:
            return Response(
                data={
                    'message': 'Quickbooks Online connection expired'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class CompanyInfoView(generics.RetrieveAPIView):
    """
    Preferences View
    """
    def get(self, request, *args, **kwargs):
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            company_info = qbo_connector.get_company_info()

            return Response(
                data=company_info,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except WrongParamsError:
            return Response(
                data={
                    'message': 'Quickbooks Online connection expired'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class DepartmentView(generics.ListCreateAPIView):
    """
    Department view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='DEPARTMENT', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get departments from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            departments = qbo_connector.sync_departments()

            return Response(
                data=self.serializer_class(departments, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomerView(generics.ListCreateAPIView):
    """
    Department view
    """

    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='CUSTOMER', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get customers from QBO
        """
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            customers = qbo_connector.sync_customers()

            return Response(
                data=self.serializer_class(customers, many=True).data,
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
            kwargs['workspace_id'], expense_group_ids)

        return Response(
            status=status.HTTP_200_OK
        )


class ChequeView(generics.ListCreateAPIView):
    """
    Create Cheque
    """
    serializer_class = ChequeSerializer

    def get_queryset(self):
        return Cheque.objects.filter(expense_group__workspace_id=self.kwargs['workspace_id']).order_by(
            '-updated_at'
        )

    def post(self, request, *args, **kwargs):
        """
        Create cheque from expense group
        """
        expense_group_id = request.data.get('expense_group_id')
        task_log_id = request.data.get('task_log_id')

        assert_valid(expense_group_id is not None, 'expense group id not found')
        assert_valid(task_log_id is not None, 'Task Log id not found')

        expense_group = ExpenseGroup.objects.get(pk=expense_group_id)
        task_log = TaskLog.objects.get(pk=task_log_id)

        create_cheque(expense_group, task_log)

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class ChequeScheduleView(generics.CreateAPIView):
    """
    Schedule cheques creation
    """

    def post(self, request, *args, **kwargs):
        expense_group_ids = request.data.get('expense_group_ids', [])

        schedule_cheques_creation(
            kwargs['workspace_id'], expense_group_ids)

        return Response(
            status=status.HTTP_200_OK
        )


class CreditCardPurchaseView(generics.ListCreateAPIView):
    """
    Create CreditCardPurchase
    """
    serializer_class = CreditCardPurchaseSerializer

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
            kwargs['workspace_id'], expense_group_ids)

        return Response(
            status=status.HTTP_200_OK
        )


class JournalEntryView(generics.ListCreateAPIView):
    """
    Create JournalEntry
    """
    serializer_class = JournalEntrySerializer

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
            kwargs['workspace_id'], expense_group_ids)

        return Response(
            status=status.HTTP_200_OK
        )


class DepartmentGroupUpdate(generics.CreateAPIView):
    serializer_class = ExpenseGroupSettingsSerializer

    def post(self, request, *args, **kwargs):
        mapping_setting = MappingSetting.objects.filter(
            destination_field='DEPARTMENT', workspace_id=kwargs['workspace_id']).first()
        expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=kwargs['workspace_id'])

        if mapping_setting:
            general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=kwargs['workspace_id'])

            reimbursable_settings = expense_group_settings.reimbursable_expense_group_fields
            if general_settings.reimbursable_expenses_object != 'JOURNAL ENTRY':
                reimbursable_settings.append(mapping_setting.source_field.lower())
                expense_group_settings.reimbursable_expense_group_fields = list(set(reimbursable_settings))

            corporate_credit_card_settings = list(expense_group_settings.corporate_credit_card_expense_group_fields)
            if general_settings.corporate_credit_card_expenses_object != 'JOURNAL ENTRY':
                corporate_credit_card_settings.append(mapping_setting.source_field.lower())
                expense_group_settings.corporate_credit_card_expense_group_fields = list(
                    set(corporate_credit_card_settings)
                )

            expense_group_settings.reimbursable_expense_group_fields = reimbursable_settings
            expense_group_settings.corporate_credit_card_expense_group_fields = corporate_credit_card_settings

            expense_group_settings.save()

        return Response(
            data=self.serializer_class(expense_group_settings).data,
            status=status.HTTP_200_OK
        )


class QuickbooksFieldsView(generics.ListAPIView):
    pagination_class = None
    serializer_class = QuickbooksFieldSerializer

    def get_queryset(self):
        attributes = DestinationAttribute.objects.filter(
            ~Q(attribute_type='EMPLOYEE') & ~Q(attribute_type='ACCOUNT') &
            ~Q(attribute_type='VENDOR') & ~Q(attribute_type='ACCOUNTS_PAYABLE') &
            ~Q(attribute_type='CREDIT_CARD_ACCOUNT') & ~Q(attribute_type='BANK_ACCOUNT'),
            workspace_id=self.kwargs['workspace_id']
        ).values('attribute_type', 'display_name').distinct()

        return attributes


class BillPaymentView(generics.CreateAPIView):
    """
    Create Bill Payment View
    """
    def post(self, request, *args, **kwargs):
        """
        Create bill payment
        """
        create_bill_payment(workspace_id=self.kwargs['workspace_id'])

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class ReimburseQuickbooksPaymentsView(generics.ListCreateAPIView):
    """
    Reimburse Quickbooks Payments View
    """
    def post(self, request, *args, **kwargs):
        """
        Process Reimbursements in Fyle
        """
        check_qbo_object_status(workspace_id=self.kwargs['workspace_id'])
        process_reimbursements(workspace_id=self.kwargs['workspace_id'])

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class SyncQuickbooksDimensionView(generics.ListCreateAPIView):
    """
    Sync Quickbooks Dimension View
    """

    def post(self, request, *args, **kwargs):

        try:
            workspace = Workspace.objects.get(id=kwargs['workspace_id'])
            if workspace.destination_synced_at:
                time_interval = datetime.now(timezone.utc) - workspace.destination_synced_at

            if workspace.destination_synced_at is None or time_interval.days > 0:
                quickbooks_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])
                quickbooks_connector = QBOConnector(quickbooks_credentials, workspace_id=kwargs['workspace_id'])

                quickbooks_connector.sync_dimensions()

                workspace.destination_synced_at = datetime.now()
                workspace.save(update_fields=['destination_synced_at'])

            return Response(
                status=status.HTTP_200_OK
            )

        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Quickbooks Credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshQuickbooksDimensionView(generics.ListCreateAPIView):
    """
    Refresh Quickbooks Dimensions view
    """

    def post(self, request, *args, **kwargs):
        """
        Sync data from quickbooks
        """
        try:
            quickbooks_credentials = QBOCredential.objects.get(workspace_id=kwargs['workspace_id'])
            quickbooks_connector = QBOConnector(quickbooks_credentials, workspace_id=kwargs['workspace_id'])

            quickbooks_connector.sync_dimensions()

            workspace = Workspace.objects.get(id=kwargs['workspace_id'])
            workspace.destination_synced_at = datetime.now()
            workspace.save(update_fields=['destination_synced_at'])

            return Response(
                status=status.HTTP_200_OK
            )

        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Quickbooks credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
