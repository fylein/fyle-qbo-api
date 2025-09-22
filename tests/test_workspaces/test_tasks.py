from fyle_accounting_mappings.models import ExpenseAttribute

from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.tasks.models import TaskLog
from apps.users.models import User
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings, WorkspaceSchedule
from apps.workspaces.tasks import (
    async_add_admins_to_workspace,
    create_admin_subscriptions,
    run_email_notification,
    run_sync_schedule,
    schedule_sync,
    update_workspace_name,
)
from tests.test_fyle.fixtures import data as fyle_data
from tests.test_workspaces.fixtures import data


def test_async_add_admins_to_workspace(db, mocker):
    old_users_count = User.objects.count()
    mocker.patch(
        'fyle.platform.apis.v1.admin.Employees.list_all',
        return_value=fyle_data['get_all_employees']
    )
    async_add_admins_to_workspace(1, 'usqywo0f3nBY')
    new_users_count = User.objects.count()

    assert new_users_count > old_users_count


def test_run_sync_schedule(mocker, db):
    workspace_id = 3
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)

    expense_group_settings.import_card_credits = True
    expense_group_settings.save()

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expenses'])
    run_sync_schedule(workspace_id)
    task_log = TaskLog.objects.filter(workspace_id=3).first()

    assert task_log.status == 'COMPLETE'

    general_settings.reimbursable_expenses_object = 'BILL'
    general_settings.corporate_credit_card_expenses_object = 'BILL'
    general_settings.save()

    run_sync_schedule(workspace_id)
    task_log = TaskLog.objects.filter(workspace_id=3).first()

    assert task_log.status == 'COMPLETE'

    general_settings.reimbursable_expenses_object = 'CHECK'
    general_settings.corporate_credit_card_expenses_object = 'DEBIT CARD EXPENSE'
    general_settings.save()

    run_sync_schedule(workspace_id)
    task_log = TaskLog.objects.filter(workspace_id=3).first()

    assert task_log.status == 'COMPLETE'

    general_settings.reimbursable_expenses_object = 'JOURNAL ENTRY'
    general_settings.corporate_credit_card_expenses_object = 'JOURNAL ENTRY'
    general_settings.save()

    run_sync_schedule(workspace_id)
    task_log = TaskLog.objects.filter(workspace_id=3).first()

    assert task_log.status == 'COMPLETE'


def test_schedule_sync(db):
    workspace_id = 3

    schedule_sync(workspace_id, True, 1, ['sample@google.com'], [], False)

    ws_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id).first()

    assert ws_schedule.schedule.func == 'apps.workspaces.tasks.run_sync_schedule'

    schedule_sync(workspace_id, False, 1, [], [], False)

    ws_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id).first()

    assert ws_schedule.schedule == None


def test_email_notification(db):
    workspace_id = 4
    ws_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id).first()
    ws_schedule.enabled = True
    ws_schedule.emails_selected = ['ashwin.t@fyle.in']
    ws_schedule.save()

    run_email_notification(workspace_id=workspace_id)

    workspace_id = 3
    ws_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id).first()
    ws_schedule.enabled = True
    ws_schedule.emails_selected = ['ashwin.t@fyle.in']
    ws_schedule.additional_email_options = [{'email': 'ashwin.t@fyle.in', 'name': 'Ashwin'}]
    ws_schedule.save()

    attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value='ashwin.t@fyle.in').first()
    attribute.value = 'ashwin333.t@fyle.in'
    attribute.save()

    run_email_notification(workspace_id=workspace_id)


def test_create_admin_subscriptions(db, mocker):
    mocker.patch(
        'fyle.platform.apis.v1.admin.Subscriptions.post',
        return_value={}
    )
    create_admin_subscriptions(3)


def test_update_workspace_name(db, mocker):
    mocker.patch(
        'apps.workspaces.tasks.get_fyle_admin',
        return_value={'data': {'org': {'name': 'Test Org'}}}
    )
    workspace = Workspace.objects.get(id=1)
    update_workspace_name(workspace.id, 'Bearer access_token')

    workspace = Workspace.objects.get(id=1)
    assert workspace.name == 'Test Org'


def test_run_sync_schedule_skips_failed_expense_groups_with_re_attempt_export_false(mocker, db):
    """
    Test that expense groups with FAILED task logs and re_attempt_export=False are skipped
    """
    workspace_id = 3

    _ = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.import_card_credits = True
    expense_group_settings.save()

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expenses'])

    mock_export = mocker.patch('apps.workspaces.actions.export_to_qbo')

    failed_expense_group = ExpenseGroup.objects.create(
        workspace_id=workspace_id,
        fund_source='PERSONAL',
        exported_at=None
    )

    TaskLog.objects.create(
        workspace_id=workspace_id,
        expense_group=failed_expense_group,
        type='CREATING_BILL',
        status='FAILED',
        re_attempt_export=False
    )

    run_sync_schedule(workspace_id)

    eligible_calls = [call for call in mock_export.call_args_list if 'expense_group_ids' in call.kwargs]
    if eligible_calls:
        exported_ids = set(eligible_calls[-1].kwargs['expense_group_ids'])
        assert failed_expense_group.id not in exported_ids, f"FAILED expense group {failed_expense_group.id} with re_attempt_export=False should be skipped"

    task_log = TaskLog.objects.filter(workspace_id=workspace_id, type='FETCHING_EXPENSES').first()
    assert task_log.status == 'COMPLETE'


def test_run_sync_schedule_includes_failed_expense_groups_with_re_attempt_export_true(mocker, db):
    """
    Test that expense groups with FAILED task logs and re_attempt_export=True are included
    """
    workspace_id = 3

    _ = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.import_card_credits = True
    expense_group_settings.save()

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expenses'])

    mock_export = mocker.patch('apps.workspaces.actions.export_to_qbo')

    retry_expense_group = ExpenseGroup.objects.create(
        workspace_id=workspace_id,
        fund_source='PERSONAL',
        exported_at=None
    )

    TaskLog.objects.create(
        workspace_id=workspace_id,
        expense_group=retry_expense_group,
        type='CREATING_BILL',
        status='FAILED',
        re_attempt_export=True
    )

    run_sync_schedule(workspace_id)

    eligible_calls = [call for call in mock_export.call_args_list if 'expense_group_ids' in call.kwargs]
    if eligible_calls:
        exported_ids = set(eligible_calls[-1].kwargs['expense_group_ids'])
        assert retry_expense_group.id in exported_ids, f"FAILED expense group {retry_expense_group.id} with re_attempt_export=True should be included"

    task_log = TaskLog.objects.filter(workspace_id=workspace_id, type='FETCHING_EXPENSES').first()
    assert task_log.status == 'COMPLETE'


def test_run_sync_schedule_includes_new_expense_groups_without_task_logs(mocker, db):
    """
    Test that new expense groups without task logs are not skipped and get included in export
    """
    workspace_id = 3

    _ = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.import_card_credits = True
    expense_group_settings.save()

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expenses'])

    mock_export = mocker.patch('apps.workspaces.actions.export_to_qbo')

    new_expense_group_1 = ExpenseGroup.objects.create(
        workspace_id=workspace_id,
        fund_source='PERSONAL',
        exported_at=None
    )

    new_expense_group_2 = ExpenseGroup.objects.create(
        workspace_id=workspace_id,
        fund_source='CCC',
        exported_at=None
    )

    run_sync_schedule(workspace_id)

    eligible_calls = [call for call in mock_export.call_args_list if 'expense_group_ids' in call.kwargs]
    if eligible_calls:
        exported_ids = set(eligible_calls[-1].kwargs['expense_group_ids'])
        assert new_expense_group_1.id in exported_ids, f"New expense group {new_expense_group_1.id} without task logs should be included"
        assert new_expense_group_2.id in exported_ids, f"New expense group {new_expense_group_2.id} without task logs should be included"

    task_log = TaskLog.objects.filter(workspace_id=workspace_id, type='FETCHING_EXPENSES').first()
    assert task_log.status == 'COMPLETE'


def test_run_sync_schedule_includes_expense_groups_with_non_failed_task_logs(mocker, db):
    """
    Test that expense groups with non-FAILED task logs are included regardless of re_attempt_export value
    """
    workspace_id = 3

    _ = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.import_card_credits = True
    expense_group_settings.save()

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expenses'])

    mock_export = mocker.patch('apps.workspaces.actions.export_to_qbo')

    ready_expense_group = ExpenseGroup.objects.create(
        workspace_id=workspace_id,
        fund_source='PERSONAL',
        exported_at=None
    )

    in_progress_expense_group = ExpenseGroup.objects.create(
        workspace_id=workspace_id,
        fund_source='PERSONAL',
        exported_at=None
    )

    TaskLog.objects.create(
        workspace_id=workspace_id,
        expense_group=ready_expense_group,
        type='CREATING_BILL',
        status='READY',
        re_attempt_export=False
    )

    TaskLog.objects.create(
        workspace_id=workspace_id,
        expense_group=in_progress_expense_group,
        type='CREATING_BILL',
        status='IN_PROGRESS',
        re_attempt_export=False
    )

    run_sync_schedule(workspace_id)

    eligible_calls = [call for call in mock_export.call_args_list if 'expense_group_ids' in call.kwargs]
    if eligible_calls:
        exported_ids = set(eligible_calls[-1].kwargs['expense_group_ids'])
        assert ready_expense_group.id in exported_ids, f"Expense group {ready_expense_group.id} with READY status should be included"
        assert in_progress_expense_group.id in exported_ids, f"Expense group {in_progress_expense_group.id} with IN_PROGRESS status should be included"

    task_log = TaskLog.objects.filter(workspace_id=workspace_id, type='FETCHING_EXPENSES').first()
    assert task_log.status == 'COMPLETE'
