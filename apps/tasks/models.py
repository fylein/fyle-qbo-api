from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.db.models import JSONField
from fyle_accounting_library.fyle_platform.constants import IMPORTED_FROM_CHOICES
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
    triggered_by = models.CharField(max_length=255, help_text="Triggered by", null=True, choices=IMPORTED_FROM_CHOICES)

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
    mapping_error_expense_group_ids = ArrayField(base_field=models.IntegerField(), default=[], help_text='list of mapping expense group ids')
    expense_attribute = models.OneToOneField(ExpenseAttribute, on_delete=models.PROTECT, null=True, help_text='Reference to Expense Attribute')
    repetition_count = models.IntegerField(help_text='repetition count for the error', default=0)
    is_resolved = models.BooleanField(default=False, help_text='Is resolved')
    error_title = models.CharField(max_length=255, help_text='Error title')
    error_detail = models.TextField(help_text='Error detail')
    is_parsed = models.BooleanField(default=False, help_text='Is parsed')
    attribute_type = models.CharField(max_length=255, null=True, blank=True, help_text='Error Attribute type')
    article_link = models.TextField(null=True, blank=True, help_text='Article link')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    def increase_repetition_count_by_one(self, is_created: bool):
        """
        Increase the repetition count by 1.
        """
        if not is_created:
            self.repetition_count += 1
            self.save()

    @staticmethod
    def get_or_create_error_with_expense_group(expense_group, expense_attribute):
        """
        Get or create an Error record and ensure that the expense_group.id
        is present in mapping_error_expense_group_ids (without duplicates).
        """
        with transaction.atomic():
            error, created = Error.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_attribute=expense_attribute,
                defaults={
                    'type': 'EMPLOYEE_MAPPING' if expense_attribute.attribute_type == 'EMPLOYEE' else 'CATEGORY_MAPPING',
                    'error_title': expense_attribute.value,
                    'error_detail': 'Employee mapping is missing' if expense_attribute.attribute_type == 'EMPLOYEE' else 'Category mapping is missing',
                    'is_resolved': False,
                    # if creating, initialize the array with the given id:
                    'mapping_error_expense_group_ids': [expense_group.id],
                }
            )

            if not created:
                if expense_group.id not in error.mapping_error_expense_group_ids:
                    error.mapping_error_expense_group_ids = list(
                        set(error.mapping_error_expense_group_ids + [expense_group.id])
                    )
                    error.save(update_fields=['mapping_error_expense_group_ids'])
            return error, created

    class Meta:
        db_table = 'errors'
