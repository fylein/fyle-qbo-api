"""
Mapping Models
"""
from django.db import models

from apps.workspaces.models import Workspace


class GeneralMapping(models.Model):
    """
    General Mappings
    """
    id = models.AutoField(primary_key=True)
    account_payable_bank_account_name = models.CharField(max_length=255, help_text='Name of the accounts payable bank '
                                                                                   'account')
    account_payable_bank_account_id = models.CharField(max_length=40, help_text='QBO accounts payable bank account id')
    bank_account_name = models.CharField(max_length=255, help_text='Name of the bank account')
    bank_account_id = models.CharField(max_length=40, help_text='QBO bank account id')
    ccc_account_name = models.CharField(max_length=255, help_text='Name of the ccc account')
    ccc_account_id = models.CharField(max_length=40, help_text='QBO ccc account id')
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')


class EmployeeMapping(models.Model):
    """
    Employee Mappings
    """
    id = models.AutoField(primary_key=True)
    employee_email = models.CharField(max_length=255, help_text='Fyle employee email')
    vendor_display_name = models.CharField(max_length=255, help_text='QBO vendor display name')
    vendor_id = models.CharField(max_length=255, help_text='QBO vendor id')
    employee_display_name = models.CharField(max_length=255, help_text='QBO employee display name')
    employee_id = models.CharField(max_length=255, help_text='QBO employee id')
    ccc_account_name = models.CharField(max_length=255, help_text='Name of the ccc account')
    ccc_account_id = models.CharField(max_length=40, help_text='QBO ccc account id')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        unique_together = ('employee_email', 'workspace')


class CategoryMapping(models.Model):
    """
    Category Mapping
    """
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=255, help_text='Fyle category')
    sub_category = models.CharField(max_length=255, help_text='Fyle sub category')
    account_name = models.CharField(max_length=255, help_text='QBO account name')
    account_id = models.CharField(max_length=255, help_text='QBO account id')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        unique_together = ('category', 'sub_category', 'workspace')


class ProjectMapping(models.Model):
    """
    Project Mapping
    """
    id = models.AutoField(primary_key=True)
    project = models.CharField(max_length=255, help_text='Fyle project')
    customer_display_name = models.CharField(max_length=255, help_text='QBO customer name')
    customer_id = models.CharField(max_length=255, help_text='QBO customer id')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        unique_together = ('project', 'workspace')


class CostCenterMapping(models.Model):
    """
    Cost Center Mapping
    """
    id = models.AutoField(primary_key=True)
    cost_center = models.CharField(max_length=255, help_text='Fyle cost center')
    class_name = models.CharField(max_length=255, help_text='QBO class name')
    class_id = models.CharField(max_length=255, help_text='QBO class id')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        unique_together = ('cost_center', 'workspace')
