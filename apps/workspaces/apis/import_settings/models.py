from django.db import models
from django.contrib.postgres.fields import ArrayField

from apps.workspaces.models import Workspace


def get_default_chart_of_accounts():
    return ['Expense']


def get_default_memo_fields():
    return ['employee_email', 'category', 'spent_on', 'report_number', 'purpose', 'expense_link']


class ImportSetting(models.Model):
    """
    Import Settings
    Schema:
    {
        "import_accounts": true,
        "chart_of_accounts": ["Expense", "Cost of Goods Sold"]
        "import_tax_codes": true,
        "import_customers": true,
        "customers_mapped_to": "PROJECT",
        "import_classes": true,
        "classes_mapped_to": "COST CENTER",
        "import_departments": true
        "departments_mapped_to": "DEPARTMENT"
    }
    """
    # Primary Key
    id = models.AutoField(primary_key=True, help_text='Unique Id to identify a workspace')

    # Foreign Keys 1-to=1 mapping
    workspace = models.OneToOneField(
        Workspace, on_delete=models.PROTECT, 
        help_text='Reference to Workspace model', 
        related_name='import_settings'
    )

    # Account Related Fields
    import_accounts = models.BooleanField(default=False, help_text='Auto import accounts to Fyle')
    charts_of_accounts = ArrayField(
        base_field=models.CharField(max_length=100), default=get_default_chart_of_accounts,
        help_text='list of chart of account types to be imported into Fyle'
    )
    account_sync_version = models.CharField(default='v1', max_length=50, help_text='Category sync version')

    # Project Related Fields
    import_customers = models.BooleanField(default=False, help_text='Auto import customers to Fyle')
    customers_mapped_to = models.CharField(max_length=50, help_text='Customer mapping field', null=True)

    # Class Related Fields
    import_classes = models.BooleanField(default=False, help_text='Auto import classes to Fyle')
    classes_mapped_to = models.CharField(max_length=50, help_text='Class mapping field', null=True)

    # Department Related Fields
    import_departments = models.BooleanField(default=False, help_text='Auto import departments to Fyle')
    departments_mapped_to = models.CharField(max_length=50, help_text='Department mapping field', null=True)

    # Taxes Related Field
    import_tax_codes = models.BooleanField(default=False, help_text='Auto import tax codes to Fyle', null=True)

    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'import_settings'
