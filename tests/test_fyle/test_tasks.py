from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.workspaces.models import FyleCredential
import pytest
from apps.fyle.tasks import schedule_expense_group_creation, create_expense_groups
from apps.tasks.models import TaskLog


def test_schedule_expense_group_creation(api_client, test_connection):
    expense_groups = ExpenseGroup.objects.filter(workspace_id=3).count()
    assert expense_groups == 17
    schedule_expense_group_creation(3)
    expense_groups = ExpenseGroup.objects.filter(workspace_id=3).count()
    assert expense_groups == 17


@pytest.mark.django_db()
def test_create_expense_groups(db):
    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=3,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=3)
    expense_group_settings.reimbursable_export_date_type = 'last_spent_at'
    expense_group_settings.ccc_export_date_type = 'last_spent_at'
    expense_group_settings.save()

    create_expense_groups(3, ['PERSONAL', 'CCC'], task_log)

    assert task_log.status == 'COMPLETE'

    fyle_credential = FyleCredential.objects.get(workspace_id=1)
    fyle_credential.delete()
    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=1,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log)

    task_log = TaskLog.objects.get(workspace_id=1)
    assert task_log.status == 'FAILED'

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=1)
    expense_group_settings.delete()

    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log)

    task_log = TaskLog.objects.get(workspace_id=1)
    assert task_log.status == 'FATAL' 



