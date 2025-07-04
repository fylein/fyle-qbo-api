"""
Mapping Models
"""
from django.db import models
from fyle_accounting_mappings.mixins import AutoAddCreateUpdateInfoMixin

from apps.workspaces.models import Workspace


class GeneralMapping(AutoAddCreateUpdateInfoMixin, models.Model):
    """
    General Mappings
    """

    id = models.AutoField(primary_key=True)
    accounts_payable_name = models.CharField(max_length=255, help_text='Accounts payable bank account name', null=True)
    accounts_payable_id = models.CharField(max_length=40, help_text='QBO accounts payable bank account id', null=True)
    qbo_expense_account_name = models.CharField(max_length=255, help_text='Name of the QBO Expense account', null=True)
    qbo_expense_account_id = models.CharField(max_length=40, help_text='QBO Expense Account id', null=True)
    bank_account_name = models.CharField(max_length=255, help_text='Name of the bank account', null=True)
    bank_account_id = models.CharField(max_length=40, help_text='QBO bank account id', null=True)
    default_ccc_account_name = models.CharField(max_length=255, help_text='Name of the default ccc account', null=True)
    default_ccc_account_id = models.CharField(max_length=40, help_text='QBO default ccc account id', null=True)
    default_debit_card_account_name = models.CharField(max_length=255, help_text='Name of the default debit card account', null=True)
    default_debit_card_account_id = models.CharField(max_length=40, help_text='QBO default debit card account id', null=True)
    default_ccc_vendor_name = models.CharField(max_length=255, help_text='QBO default CCC Vendor Name', null=True)
    default_ccc_vendor_id = models.CharField(max_length=255, help_text='QBO default CCC Vendor ID', null=True)
    default_tax_code_name = models.CharField(max_length=255, help_text='QBO default Tax Code name', null=True)
    default_tax_code_id = models.CharField(max_length=255, help_text='QBO default Tax Code ID', null=True)
    bill_payment_account_id = models.CharField(max_length=255, help_text='BillPayment Account id', null=True)
    bill_payment_account_name = models.CharField(max_length=255, help_text='BillPayment Account name', null=True)
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model', related_name='general_mappings')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'general_mappings'
