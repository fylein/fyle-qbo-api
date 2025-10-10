"""
Workspace Models
"""
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.cache import cache
from django.db import models
from django.db.models import JSONField
from django_q.models import Schedule

from apps.workspaces.enums import CacheKeyEnum
from fyle_accounting_mappings.mixins import AutoAddCreateUpdateInfoMixin

User = get_user_model()


ONBOARDING_STATE_CHOICES = (
    ('CONNECTION', 'CONNECTION'),
    ('EXPORT_SETTINGS', 'EXPORT_SETTINGS'),
    ('IMPORT_SETTINGS', 'IMPORT_SETTINGS'),
    ('ADVANCED_CONFIGURATION', 'ADVANCED_CONFIGURATION'),
    ('COMPLETE', 'COMPLETE'),
)

APP_VERSION_CHOICES = (('v1', 'v1'), ('v2', 'v2'))

EXPORT_MODE_CHOICES = (('MANUAL', 'MANUAL'), ('AUTO', 'AUTO'))

NAME_IN_JOURNAL_ENTRY = (
    ('MERCHANT', 'MERCHANT'),
    ('EMPLOYEE', 'EMPLOYEE')
)

CODE_CHOICES = (
    ('ACCOUNT', 'ACCOUNT'),
)


def get_default_onboarding_state():
    return 'CONNECTION'


class Workspace(models.Model):
    """
    Workspace model
    """

    id = models.AutoField(primary_key=True, help_text='Unique Id to identify a workspace')
    name = models.CharField(max_length=255, help_text='Name of the workspace')
    user = models.ManyToManyField(User, help_text='Reference to users table')
    fyle_org_id = models.CharField(max_length=255, help_text='org id', unique=True)
    fyle_currency = models.CharField(max_length=5, help_text='Fyle Currency', null=True)
    qbo_realm_id = models.CharField(max_length=255, help_text='qbo realm id', null=True)
    cluster_domain = models.CharField(max_length=255, help_text='fyle cluster domain', null=True)
    app_version = models.CharField(max_length=2, help_text='App version', default='v2', choices=APP_VERSION_CHOICES)
    last_synced_at = models.DateTimeField(help_text='Datetime when expenses were pulled last', null=True)
    ccc_last_synced_at = models.DateTimeField(help_text='Datetime when ccc expenses were pulled last', null=True)
    source_synced_at = models.DateTimeField(help_text='Datetime when source dimensions were pulled', null=True)
    destination_synced_at = models.DateTimeField(help_text='Datetime when destination dimensions were pulled', null=True)
    onboarding_state = models.CharField(max_length=50, choices=ONBOARDING_STATE_CHOICES, default=get_default_onboarding_state, help_text='Onboarding status of the workspace', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'workspaces'


class WorkspaceSchedule(models.Model):
    """
    Workspace Schedule
    """

    id = models.AutoField(primary_key=True, help_text='Unique Id to identify a schedule')
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model', related_name='workspace_schedules')
    enabled = models.BooleanField(default=False)
    start_datetime = models.DateTimeField(help_text='Datetime for start of schedule', null=True)
    interval_hours = models.IntegerField(null=True)
    error_count = models.IntegerField(null=True, help_text='Number of errors in export')
    additional_email_options = JSONField(default=list, help_text='Email and Name of person to send email', null=True)
    emails_selected = ArrayField(base_field=models.CharField(max_length=255), null=True, help_text='Emails that has to be send mail')
    is_real_time_export_enabled = models.BooleanField(default=False)
    schedule = models.OneToOneField(Schedule, on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, null=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'workspace_schedules'


def get_default_chart_of_accounts():
    return ['Expense']


def get_default_memo_fields():
    return ['employee_email', 'category', 'spent_on', 'report_number', 'purpose', 'expense_link']


class WorkspaceGeneralSettings(AutoAddCreateUpdateInfoMixin, models.Model):
    """
    Workspace General Settings
    """

    id = models.AutoField(primary_key=True, help_text='Unique Id to identify a workspace')
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model', related_name='workspace_general_settings')
    reimbursable_expenses_object = models.CharField(max_length=50, help_text='Reimbursable Expenses type', null=True)
    corporate_credit_card_expenses_object = models.CharField(max_length=50, help_text='Non Reimbursable Expenses type', null=True)
    employee_field_mapping = models.CharField(max_length=50, help_text='Mapping Settings ( VENDOR / EMPLOYEE )')
    map_merchant_to_vendor = models.BooleanField(help_text='Map Merchant to Vendor for CCC Expenses', default=False)
    import_categories = models.BooleanField(default=False, help_text='Auto import Categories to Fyle')
    import_items = models.BooleanField(default=False, help_text='Auto import Items to Fyle')
    import_projects = models.BooleanField(default=False, help_text='Auto import projects to Fyle')
    import_tax_codes = models.BooleanField(default=False, help_text='Auto import tax codes to Fyle', null=True)
    change_accounting_period = models.BooleanField(default=True, help_text='Export Expense when accounting period is closed')
    charts_of_accounts = ArrayField(base_field=models.CharField(max_length=100), default=get_default_chart_of_accounts, help_text='list of chart of account types to be imported into Fyle')
    memo_structure = ArrayField(base_field=models.CharField(max_length=100), default=get_default_memo_fields, help_text='list of system fields for creating custom memo')
    auto_map_employees = models.CharField(max_length=50, help_text='Auto Map Employees type from QBO to Fyle', null=True)
    auto_create_destination_entity = models.BooleanField(default=False, help_text='Auto create vendor / employee')
    auto_create_merchants_as_vendors = models.BooleanField(default=False, help_text='Auto create Fyle Merchants as QBO vendors')
    sync_fyle_to_qbo_payments = models.BooleanField(default=False, help_text='Auto Sync Payments from Fyle to QBO')
    sync_qbo_to_fyle_payments = models.BooleanField(default=False, help_text='Auto Sync Payments from QBO to Fyle')
    category_sync_version = models.CharField(default='v2', max_length=50, help_text='Category sync version')
    je_single_credit_line = models.BooleanField(default=False, help_text='Single Credit Line for Journal Entries')
    map_fyle_cards_qbo_account = models.BooleanField(default=True, help_text='Map Fyle Cards to QBO Accounts')
    import_vendors_as_merchants = models.BooleanField(default=False, help_text='Auto import vendors from qbo as merchants to Fyle')
    is_multi_currency_allowed = models.BooleanField(default=False, help_text='Multi Currency Allowed')
    name_in_journal_entry = models.CharField(
        max_length=100,
        help_text='Name in journal entry for ccc expense only',
        default='EMPLOYEE',choices=NAME_IN_JOURNAL_ENTRY)
    import_code_fields = ArrayField(
        base_field=models.CharField(
            max_length=255,
            choices=CODE_CHOICES
        ),
        help_text='Code Preference List',
        blank=True,
        default=list
    )
    skip_accounting_export_summary_post = models.BooleanField(default=False, help_text='Skip accounting export summary post')
    is_sync_after_timestamp_enabled = models.BooleanField(default=True, help_text='Sync after timestamp enabled')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'workspace_general_settings'


class QBOCredential(models.Model):
    """
    Table to store QBO credentials
    """

    id = models.AutoField(primary_key=True)
    refresh_token = models.TextField(help_text='Stores QBO refresh token', null=True)
    realm_id = models.CharField(max_length=40, help_text='QBO realm / company Id', null=True)
    is_expired = models.BooleanField(default=False, help_text='QBO token expiry flag')
    company_name = models.CharField(max_length=255, help_text='QBO Company Name', null=True)
    country = models.CharField(max_length=255, help_text='QBO Country Name', null=True)
    currency = models.CharField(max_length=255, help_text='QBO Currency', null=True)
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'qbo_credentials'

    @staticmethod
    def get_active_qbo_credentials(workspace_id):
        return QBOCredential.objects.get(workspace_id=workspace_id, is_expired=False, refresh_token__isnull=False)


class FyleCredential(models.Model):
    """
    Table to store Fyle credentials
    """

    id = models.AutoField(primary_key=True)
    refresh_token = models.TextField(help_text='Stores Fyle refresh token')
    cluster_domain = models.CharField(max_length=255, help_text='Cluster Domain', null=True)
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'fyle_credentials'


class LastExportDetail(models.Model):
    """
    Table to store Last Export Details
    """

    id = models.AutoField(primary_key=True)
    last_exported_at = models.DateTimeField(help_text='Last exported at datetime', null=True)
    next_export_at = models.DateTimeField(help_text='Next export datetime', null=True)
    export_mode = models.CharField(max_length=50, help_text='Mode of the export Auto / Manual', choices=EXPORT_MODE_CHOICES, null=True)
    total_expense_groups_count = models.IntegerField(help_text='Total count of expense groups exported', null=True)
    successful_expense_groups_count = models.IntegerField(help_text='count of successful expense_groups ', null=True)
    failed_expense_groups_count = models.IntegerField(help_text='count of failed expense_groups ', null=True)
    unmapped_card_count = models.IntegerField(help_text='count of unmapped card', default=0)
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'last_export_details'


class FeatureConfig(models.Model):
    """
    Table to store Feature configs
    """
    id = models.AutoField(primary_key=True)
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    export_via_rabbitmq = models.BooleanField(default=True, help_text='Enable export via rabbitmq')
    import_via_rabbitmq = models.BooleanField(default=True, help_text='Enable import via rabbitmq')
    fyle_webhook_sync_enabled = models.BooleanField(default=False, help_text='Enable fyle attribute webhook sync')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    @classmethod
    def get_cached_response(cls, workspace_id: int):
        """
        Get cached feature config for workspace
        Cache for 48 hours (172800 seconds)
        :param workspace_id: workspace id
        :return: FeatureConfig instance
        """
        cache_key = CacheKeyEnum.FEATURE_CONFIG.value.format(workspace_id=workspace_id)
        cached_feature_config = cache.get(cache_key)

        if cached_feature_config:
            return cached_feature_config

        feature_config = cls.objects.get(workspace_id=workspace_id)
        cache.set(cache_key, feature_config, 172800)
        return feature_config

    class Meta:
        db_table = 'feature_configs'
