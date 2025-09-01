from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.workspaces.apis.export_settings.helpers import clear_workspace_errors_on_export_type_change


def test_clear_workspace_errors_no_changes(setup_test_data_for_export_settings):
    """
    Test when no export settings change - uses existing workspace data
    """
    workspace_id = 1

    old_config = {
        'reimbursable_expenses_object': 'EXPENSE',
        'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
    }

    new_config = {
        'reimbursable_expenses_object': 'EXPENSE',
        'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
    }

    setup_test_data_for_export_settings(workspace_id, new_config)

    clear_workspace_errors_on_export_type_change(
        workspace_id, old_config, new_config
    )

    enqueued_exists = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status='ENQUEUED',
        type='CREATING_EXPENSE'
    ).exists()
    assert enqueued_exists is True


def test_clear_workspace_errors_with_mapping_errors(
    setup_test_data_for_export_settings,
    create_expense_groups,
    create_mapping_errors,
    create_task_logs
):
    """
    Test mapping error handling when reimbursable expenses object changes
    """
    workspace_id = 2
    setup_test_data_for_export_settings(workspace_id)

    expense_group_configs = [
        {'id': 201, 'fund_source': 'PERSONAL', 'exported_at': None},
        {'id': 202, 'fund_source': 'CCC', 'exported_at': None}
    ]
    create_expense_groups(workspace_id, expense_group_configs)

    error_configs = [
        {
            'type': 'EMPLOYEE_MAPPING',
            'attribute_type': 'EMPLOYEE',
            'display_name': 'Employee',
            'value': 'test.employee2@example.com',
            'mapping_error_expense_group_ids': [201, 202],
            'error_title': 'test.employee@example.com',
            'error_detail': 'Employee mapping is missing',
            'is_resolved': False
        },
        {
            'type': 'INTACCT_ERROR',
            'expense_group_id': 201,
            'error_title': 'Export failed',
            'error_detail': 'Some export error'
        }
    ]
    errors = create_mapping_errors(workspace_id, error_configs)
    mapping_error = errors[0]
    direct_error = errors[1]

    task_log_configs = [
        {
            'expense_group_id': 201,
            'status': 'FAILED',
            'type': 'CREATING_EXPENSE'
        }
    ]
    create_task_logs(workspace_id, task_log_configs)

    old_config = {
        'reimbursable_expenses_object': 'EXPENSE',
        'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
    }

    new_config = {
        'reimbursable_expenses_object': 'BILL',
        'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
    }

    workspace_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_settings.reimbursable_expenses_object = 'BILL'
    workspace_settings.corporate_credit_card_expenses_object = 'CREDIT CARD PURCHASE'
    workspace_settings.save()

    clear_workspace_errors_on_export_type_change(
        workspace_id, old_config, new_config
    )

    mapping_error.refresh_from_db()
    assert mapping_error.mapping_error_expense_group_ids == [202]

    direct_error_exists = Error.objects.filter(id=direct_error.id).exists()
    assert direct_error_exists is False

    task_log_exists = TaskLog.objects.filter(
        workspace_id=workspace_id,
        expense_group_id=201,
        status='FAILED'
    ).exists()
    assert task_log_exists is False


def test_clear_workspace_errors_enqueued_tasks_deleted_on_change(
    setup_test_data_for_export_settings,
    create_expense_groups,
    create_task_logs
):
    """
    Test that ENQUEUED task logs are deleted when export settings change
    """
    workspace_id = 3
    setup_test_data_for_export_settings(workspace_id)

    expense_group_configs = [
        {'id': 501, 'fund_source': 'PERSONAL', 'exported_at': None}
    ]
    create_expense_groups(workspace_id, expense_group_configs)

    # Create task logs
    task_log_configs = [
        {'status': 'ENQUEUED', 'type': 'CREATING_EXPENSE'},
        {'status': 'ENQUEUED', 'type': 'CREATING_BILL'},
        {'status': 'ENQUEUED', 'type': 'FETCHING_EXPENSES'}
    ]
    create_task_logs(workspace_id, task_log_configs)

    old_config = {
        'reimbursable_expenses_object': 'EXPENSE',
        'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
    }

    new_config = {
        'reimbursable_expenses_object': 'BILL',
        'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
    }

    # Create the workspace settings for test setup
    WorkspaceGeneralSettings.objects.get_or_create(
        workspace_id=workspace_id,
        defaults=new_config
    )

    clear_workspace_errors_on_export_type_change(
        workspace_id, old_config, new_config
    )

    enqueued_count = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status='ENQUEUED'
    ).exclude(type__in=['FETCHING_EXPENSES', 'CREATING_BILL_PAYMENT']).count()
    assert enqueued_count == 0

    excluded_exists = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status='ENQUEUED',
        type='FETCHING_EXPENSES'
    ).exists()
    assert excluded_exists is True


def test_clear_workspace_errors_complete_mapping_deletion(
    setup_test_data_for_export_settings,
    create_expense_groups,
    create_mapping_errors
):
    """
    Test when mapping error should be completely deleted (no remaining expense groups)
    """
    workspace_id = 4
    setup_test_data_for_export_settings(workspace_id)

    expense_group_configs = [
        {'id': 301, 'fund_source': 'PERSONAL', 'exported_at': None}
    ]
    create_expense_groups(workspace_id, expense_group_configs)

    error_configs = [
        {
            'type': 'CATEGORY_MAPPING',
            'attribute_type': 'CATEGORY',
            'display_name': 'Category',
            'value': 'Travel-Test',
            'mapping_error_expense_group_ids': [301],
            'error_title': 'Travel',
            'error_detail': 'Category mapping is missing'
        }
    ]
    errors = create_mapping_errors(workspace_id, error_configs)
    mapping_error = errors[0]

    old_config = {
        'reimbursable_expenses_object': 'EXPENSE',
        'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
    }

    new_config = {
        'reimbursable_expenses_object': 'BILL',
        'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
    }

    WorkspaceGeneralSettings.objects.get_or_create(
        workspace_id=workspace_id,
        defaults=new_config
    )

    clear_workspace_errors_on_export_type_change(
        workspace_id, old_config, new_config
    )

    mapping_error_exists = Error.objects.filter(id=mapping_error.id).exists()
    assert mapping_error_exists is False


def test_clear_workspace_errors_tax_mapping_handling(
    setup_test_data_for_export_settings,
    create_expense_groups,
    create_mapping_errors
):
    """
    Test that TAX_MAPPING errors are handled correctly
    """
    workspace_id = 5
    setup_test_data_for_export_settings(workspace_id)

    expense_group_configs = [
        {'id': 401, 'fund_source': 'PERSONAL', 'exported_at': None},
        {'id': 402, 'fund_source': 'CCC', 'exported_at': None}
    ]
    create_expense_groups(workspace_id, expense_group_configs)

    error_configs = [
        {
            'type': 'TAX_MAPPING',
            'attribute_type': 'TAX_GROUP',
            'display_name': 'Tax Group',
            'value': 'GST 10%',
            'mapping_error_expense_group_ids': [401, 402],
            'error_title': 'GST 10%',
            'error_detail': 'Tax Group mapping is missing'
        }
    ]
    errors = create_mapping_errors(workspace_id, error_configs)
    tax_mapping_error = errors[0]

    old_config = {
        'reimbursable_expenses_object': 'EXPENSE',
        'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
    }

    new_config = {
        'reimbursable_expenses_object': 'BILL',
        'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
    }

    WorkspaceGeneralSettings.objects.get_or_create(
        workspace_id=workspace_id,
        defaults=new_config
    )

    clear_workspace_errors_on_export_type_change(
        workspace_id, old_config, new_config
    )

    tax_mapping_error.refresh_from_db()
    assert tax_mapping_error.mapping_error_expense_group_ids == [402]
