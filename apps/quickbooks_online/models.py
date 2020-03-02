"""
QBO models
"""
from datetime import datetime

from django.db import models

from apps.fyle.models import ExpenseGroup, Expense
from apps.mappings.models import GeneralMapping, EmployeeMapping, CategoryMapping, CostCenterMapping, ProjectMapping


class Bill(models.Model):
    """
    QBO Bill
    """
    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    accounts_payable_id = models.CharField(max_length=255, help_text='QBO Accounts Payable account id')
    vendor_id = models.CharField(max_length=255, help_text='QBO vendor id')
    department_id = models.CharField(max_length=255, help_text='QBO department id', null=True)
    transaction_date = models.DateField(help_text='Bill transaction date')
    currency = models.CharField(max_length=5, help_text='Bill Currency')
    private_note = models.TextField(help_text='Bill Description')
    bill_number = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_bill(expense_group: ExpenseGroup):
        """
        Create bill
        :param expense_group: expense group
        :return: bill object
        """
        description = expense_group.description

        expense = expense_group.expenses.first()

        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
        bill_object, _ = Bill.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'accounts_payable_id': general_mappings.bank_account_id,
                'vendor_id': EmployeeMapping.objects.get(employee_email=description.get('employee_email')).vendor_id,
                'department_id': None,
                'transaction_date': datetime.now().strftime("%Y-%m-%d"),
                'private_note': 'Report {0} / {1} exported on {2}'.format(
                    expense.claim_number, expense.report_id, datetime.now().strftime("%Y-%m-%d")
                ),
                'bill_number': expense_group.fyle_group_id
            }
        )
        return bill_object


class BillLineitem(models.Model):
    """
    QBO Bill Lineitem
    """
    id = models.AutoField(primary_key=True)
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, help_text='Reference to bill')
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    account_id = models.CharField(max_length=255, help_text='QBO account id')
    class_id = models.CharField(max_length=255, help_text='QBO class id', null=True)
    customer_id = models.CharField(max_length=255, help_text='QBO customer id', null=True)
    amount = models.FloatField(help_text='Bill amount')
    description = models.CharField(max_length=255, help_text='QBO bill lineitem description', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_bill_lineitems(expense_group: ExpenseGroup):
        """
        Create bill lineitems
        :param expense_group: expense group
        :return: lineitems objects
        """
        expenses = expense_group.expenses.all()
        bill = Bill.objects.get(expense_group=expense_group)

        bill_lineitem_objects = []

        for lineitem in expenses:
            account = CategoryMapping.objects.filter(category=lineitem.category,
                                                     sub_category=lineitem.sub_category).first()

            cost_center_mapping = CostCenterMapping.objects.filter(
                cost_center=lineitem.cost_center, workspace_id=expense_group.workspace_id).first()

            project_mapping = ProjectMapping.objects.filter(
                project=lineitem.project, workspace_id=expense_group.workspace_id).first()

            class_id = cost_center_mapping.class_id if cost_center_mapping else None

            customer_id = project_mapping.customer_id if project_mapping else None

            bill_lineitem_object, _ = BillLineitem.objects.update_or_create(
                bill=bill,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.account_id if account else None,
                    'class_id': class_id,
                    'customer_id': customer_id,
                    'amount': lineitem.amount,
                    'description': lineitem.purpose
                }
            )

            bill_lineitem_objects.append(bill_lineitem_object)

        return bill_lineitem_objects
