import json
from unittest import mock

from django.db.models import Q
from django.urls import reverse

import pytest

from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.fyle.tasks import (
    create_expense_groups,
    post_accounting_export_summary,
    import_and_export_expenses
)
from apps.fyle.actions import mark_expenses_as_skipped
from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential, Workspace
from tests.helper import dict_compare_keys
from tests.test_fyle.fixtures import data


@pytest.mark.django_db()
def test_create_expense_groups(mocker, db):
    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expenses'])

    task_log, _ = TaskLog.objects.update_or_create(workspace_id=3, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=3)
    expense_group_settings.reimbursable_export_date_type = 'last_spent_at'
    expense_group_settings.ccc_export_date_type = 'last_spent_at'
    expense_group_settings.import_card_credits = True
    expense_group_settings.save()

    create_expense_groups(3, ['PERSONAL', 'CCC'], task_log)

    assert task_log.status == 'COMPLETE'

    fyle_credential = FyleCredential.objects.get(workspace_id=1)
    fyle_credential.delete()
    task_log, _ = TaskLog.objects.update_or_create(workspace_id=1, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log)

    task_log = TaskLog.objects.get(workspace_id=1)
    assert task_log.status == 'FAILED'

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=1)
    expense_group_settings.delete()

    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log)

    task_log = TaskLog.objects.get(workspace_id=1)
    assert task_log.status == 'FATAL'


@pytest.mark.django_db()
def test_create_expense_group_skipped_flow(mocker, api_client, test_connection):
    access_token = test_connection.access_token
    # adding the expense-filter
    url = reverse('expense-filters', kwargs={'workspace_id': 1})

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url, data=data['expense_filter_0'])
    assert response.status_code == 201
    response = json.loads(response.content)

    assert dict_compare_keys(response, data['expense_filter_0_response']) == [], 'expense group api return diffs in keys'
    task_log, _ = TaskLog.objects.update_or_create(workspace_id=1, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=1)
    expense_group_settings.import_card_credits = True
    expense_group_settings.save()

    with mock.patch('fyle_integrations_platform_connector.apis.Expenses.get') as mock_call:
        mock_call.side_effect = [data['expenses'], data['ccc_expenses']]

        expense_group_count = len(ExpenseGroup.objects.filter(workspace_id=1))
        expenses_count = len(Expense.objects.filter(org_id='or79Cob97KSh'))

        create_expense_groups(1, ['PERSONAL', 'CCC'], task_log)
        expense_group = ExpenseGroup.objects.filter(workspace_id=1)
        expenses = Expense.objects.filter(org_id='or79Cob97KSh')

        assert len(expense_group) == expense_group_count
        assert len(expenses) == expenses_count

        for expense in expenses:
            if expense.employee_email == 'jhonsnow@fyle.in':
                assert expense.is_skipped == True


def test_post_accounting_export_summary(db, mocker):
    expense_group = ExpenseGroup.objects.filter(workspace_id=3).first()
    expense_id = expense_group.expenses.first().id
    expense_group.expenses.remove(expense_id)

    workspace = Workspace.objects.get(id=3)

    expense = Expense.objects.filter(id=expense_id).first()
    expense.workspace_id = 3
    expense.save()

    mark_expenses_as_skipped(Q(), [expense_id], workspace)

    assert Expense.objects.filter(id=expense_id).first().accounting_export_summary['synced'] == False

    mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.post_bulk_accounting_export_summary',
        return_value=[]
    )
    post_accounting_export_summary('or79Cob97KSh', 3)

    assert Expense.objects.filter(id=expense_id).first().accounting_export_summary['synced'] == True


def test_import_and_export_expenses(db):
    import_and_export_expenses('rp1s1L3QtMpF', 'or79Cob97KSh')
