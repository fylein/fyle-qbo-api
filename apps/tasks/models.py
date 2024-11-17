from django.db import models
from django.db.models import JSONField
from fyle_accounting_mappings.models import ExpenseAttribute

from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.models import Bill, BillPayment, Cheque, CreditCardPurchase, JournalEntry, QBOExpense
from apps.workspaces.models import Workspace


def get_default():
    return {'default': 'default value'}


class TaskLog(models.Model):
    """
    Table to store task logs
    """

    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    type = models.CharField(max_length=50, help_text='Task type (FETCH_EXPENSES / CREATE_BILL / CREATE_CHECK)')
    task_id = models.CharField(max_length=255, null=True, help_text='Django Q task reference')
    expense_group = models.ForeignKey(ExpenseGroup, on_delete=models.PROTECT, null=True, help_text='Reference to Expense group', unique=True)
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, help_text='Reference to Bill', null=True)
    cheque = models.ForeignKey(Cheque, on_delete=models.PROTECT, help_text='Reference to Cheque', null=True)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.PROTECT, help_text='Reference to journal_entry', null=True)
    credit_card_purchase = models.ForeignKey(CreditCardPurchase, on_delete=models.PROTECT, help_text='Reference to CreditCardPurchase', null=True)
    qbo_expense = models.ForeignKey(QBOExpense, on_delete=models.PROTECT, help_text='Reference to QBO Expense', null=True)
    bill_payment = models.ForeignKey(BillPayment, on_delete=models.PROTECT, help_text='Reference to BillPayment', null=True)
    status = models.CharField(max_length=255, help_text='Task Status')
    detail = JSONField(help_text='Task response', null=True, default=get_default)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    quickbooks_errors = JSONField(help_text='Quickbooks Errors', null=True)
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'task_logs'


ERROR_TYPE_CHOICES = (('EMPLOYEE_MAPPING', 'EMPLOYEE_MAPPING'), ('CATEGORY_MAPPING', 'CATEGORY_MAPPING'), ('TAX_MAPPING', 'TAX_MAPPING'), ('QBO_ERROR', 'QBO_ERROR'))


class Error(models.Model):
    """
    Table to store errors
    """

    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    type = models.CharField(max_length=50, choices=ERROR_TYPE_CHOICES, help_text='Error type')
    expense_group = models.ForeignKey(ExpenseGroup, on_delete=models.PROTECT, null=True, help_text='Reference to Expense group')
    expense_attribute = models.OneToOneField(ExpenseAttribute, on_delete=models.PROTECT, null=True, help_text='Reference to Expense Attribute')
    repetition_count = models.IntegerField(help_text='repetition count for the error', default=0)
    is_resolved = models.BooleanField(default=False, help_text='Is resolved')
    error_title = models.CharField(max_length=255, help_text='Error title')
    error_detail = models.TextField(help_text='Error detail')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    def increase_repetition_count_by_one(self, is_created: bool):
        """
        Increase the repetition count by 1.
        """
        if not is_created:
            self.repetition_count += 1
            self.save()

    class Meta:
        db_table = 'errors'
