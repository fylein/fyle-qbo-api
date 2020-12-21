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
    accounts_payable_name = models.CharField(max_length=255, help_text='Accounts payable bank account name', null=True)
    accounts_payable_id = models.CharField(max_length=40, help_text='QBO accounts payable bank account id', null=True)
    bank_account_name = models.CharField(max_length=255, help_text='Name of the bank account', null=True)
    bank_account_id = models.CharField(max_length=40, help_text='QBO bank account id', null=True)
    default_ccc_account_name = models.CharField(max_length=255, help_text='Name of the default ccc account', null=True)
    default_ccc_account_id = models.CharField(max_length=40, help_text='QBO default ccc account id', null=True)
    default_ccc_vendor_name = models.CharField(max_length=255, help_text='QBO default CCC Vendor Name', null=True)
    default_ccc_vendor_id = models.CharField(max_length=255, help_text='QBO default CCC Vendor ID', null=True)
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'general_mappings'


class EmployeeMapping(models.Model):
    """
    Employee Mappings
    """
    id = models.AutoField(primary_key=True)
    employee_email = models.CharField(max_length=255, help_text='Fyle employee email')
    vendor_display_name = models.CharField(max_length=255, help_text='QBO vendor display name', null=True)
    vendor_id = models.CharField(max_length=255, help_text='QBO vendor id', null=True)
    employee_display_name = models.CharField(max_length=255, help_text='QBO employee display name', null=True)
    employee_id = models.CharField(max_length=255, help_text='QBO employee id', null=True)
    ccc_account_name = models.CharField(max_length=255, help_text='Name of the ccc account', null=True)
    ccc_account_id = models.CharField(max_length=40, help_text='QBO ccc account id', null=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        unique_together = ('employee_email', 'workspace')
        db_table = 'employee_mappings'


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
        db_table = 'category_mappings'


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
        db_table = 'project_mappings'


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
        db_table = 'cost_center_mappings'
