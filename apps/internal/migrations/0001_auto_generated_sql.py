# Generated by Django
from django.db import migrations
from apps.internal.helpers import safe_run_sql
sql_files = [
    # Global Shared Functions
    'fyle-integrations-db-migrations/common/global_shared/functions/json_diff.sql',
    'fyle-integrations-db-migrations/common/global_shared/functions/log_delete_event.sql',

    # Grouped Functions
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/functions/delete_failed_expenses_qbo_intacct_xero_netsuite.sql',
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/functions/delete_test_orgs_schedule.sql',
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/functions/log_update_event.sql',
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/functions/trigger_auto_import_export.sql',
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/functions/update_in_progress_tasks_to_failed.sql',
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/functions/ws_org_id.sql',
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/functions/ws_search.sql',

    # Global Views
    'fyle-integrations-db-migrations/common/global_shared/views/extended_category_mappings_view.sql',
    'fyle-integrations-db-migrations/common/global_shared/views/extended_employee_mappings_view.sql',
    'fyle-integrations-db-migrations/common/global_shared/views/extended_mappings_view.sql',
    'fyle-integrations-db-migrations/common/global_shared/views/prod_workspaces_view.sql',

    # Global Alert Views
    'fyle-integrations-db-migrations/common/global_shared/views/alerts/_import_logs_fatal_failed_in_progress_tasks_view.sql',
    'fyle-integrations-db-migrations/common/global_shared/views/alerts/import_logs_fatal_failed_in_progress_tasks_view.sql',
    'fyle-integrations-db-migrations/common/global_shared/views/alerts/ormq_count_view.sql',
    'fyle-integrations-db-migrations/common/global_shared/views/alerts/repetition_error_count_view.sql',

    # Grouped Views
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/views/prod_active_workspaces_view.sql',
    # Grouped Alert Views
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/views/alerts/_django_queue_fatal_tasks_view.sql',
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/views/alerts/_django_queue_in_progress_tasks_view.sql',
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/views/alerts/django_queue_fatal_tasks_view.sql',
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/views/alerts/django_queue_in_progress_tasks_view.sql',
    'fyle-integrations-db-migrations/common/qbo_intacct_netsuite_xero/views/alerts/inactive_workspaces_view.sql',

    # QBO Specific Functions
    'fyle-integrations-db-migrations/qbo/functions/delete_workspace.sql',
    'fyle-integrations-db-migrations/qbo/functions/re_export_expenses_qbo.sql',
    'fyle-integrations-db-migrations/qbo/functions/remove_inactive_org_schedules.sql',
    'fyle-integrations-db-migrations/qbo/functions/trigger_auto_import.sql',

    # QBO Specific Views
    'fyle-integrations-db-migrations/qbo/views/extended_expenses_view.sql',
    'fyle-integrations-db-migrations/qbo/views/extended_settings_view.sql',
    'fyle-integrations-db-migrations/qbo/views/product_advance_settings_view.sql',
    'fyle-integrations-db-migrations/qbo/views/product_export_settings_view.sql',
    'fyle-integrations-db-migrations/qbo/views/product_import_settings_view.sql',

    'fyle-integrations-db-migrations/common/global_shared/helpers/add-replication-identity.sql',
    'fyle-integrations-db-migrations/qbo/helpers/add-tables-to-publication.sql'
]


class Migration(migrations.Migration):
    dependencies = [
        ('fyle', '0041_auto_20241226_1155'),
        ('mappings', '0011_auto_20241226_1155'),
        ('quickbooks_online', '0018_creditcardpurchase_exchange_rate'),
        ('tasks', '0013_alter_tasklog_expense_group'),
        ('users', '0002_auto_20201228_0715'),
        ('workspaces', '0052_workspacegeneralsettings_skip_accounting_export_summary_post')
    ]  # This is the first migration
    operations = safe_run_sql(sql_files)
