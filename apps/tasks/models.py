from django.db import models
from django.contrib.postgres.fields import JSONField

from apps.workspaces.models import Workspace
from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.models import Bill, Cheque, CreditCardPurchase, JournalEntry, BillPayment


def get_default():
    return {
        'default': 'default value'
    }


class TaskLog(models.Model):
    """
    Table to store task logs
    """
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    type = models.CharField(max_length=50, help_text='Task type (FETCH_EXPENSES / CREATE_BILL / CREATE_CHECK)')
    task_id = models.CharField(max_length=255, null=True, help_text='Django Q task reference')
    expense_group = models.ForeignKey(ExpenseGroup, on_delete=models.PROTECT, unique=True,
                                      null=True, help_text='Reference to Expense group')
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, help_text='Reference to Bill', null=True)
    cheque = models.ForeignKey(Cheque, on_delete=models.PROTECT, help_text='Reference to Cheque', null=True)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.PROTECT,
                                      help_text='Reference to journal_entry', null=True)
    credit_card_purchase = models.ForeignKey(CreditCardPurchase, on_delete=models.PROTECT,
                                             help_text='Reference to CreditCardPurchase', null=True)
    bill_payment = models.ForeignKey(BillPayment, on_delete=models.PROTECT, help_text='Reference to BillPayment', null=True)
    status = models.CharField(max_length=255, help_text='Task Status')
    detail = JSONField(help_text='Task response', null=True, default=get_default)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'task_logs'
