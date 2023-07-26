from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_integrations_platform_connector import PlatformConnector

from apps.fyle.models import ExpenseGroupSettings
from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceGeneralSettings, WorkspaceSchedule
from apps.workspaces.tasks import run_email_notification, run_sync_schedule, \
    schedule_sync, async_add_admins_to_workspace
from apps.users.models import User

from tests.test_workspaces.fixtures import data
from ..test_fyle.fixtures import data as fyle_data


def test_async_add_admins_to_workspace(db, mocker):
    old_users_count = User.objects.count()
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Employees.list_all',
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

    schedule_sync(workspace_id, True, 1, ['sample@google.com'], [])

    ws_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id).first()

    assert ws_schedule.schedule.func == 'apps.workspaces.tasks.run_sync_schedule'

    schedule_sync(workspace_id, False, 1, [], [])

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
