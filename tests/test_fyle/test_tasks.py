import json
from unittest import mock

import pytest
from django.db.models import Q
from django.urls import reverse
from fyle.platform.exceptions import InternalServerError, InvalidTokenError, RetryException
from rest_framework import status
from rest_framework.exceptions import ValidationError
from apps.fyle.actions import mark_expenses_as_skipped
from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings, ExpenseFilter
from apps.fyle.tasks import (
    create_expense_groups,
    import_and_export_expenses,
    post_accounting_export_summary,
    sync_dimensions,
    update_non_exported_expenses,
    re_run_skip_export_rule,
)
from apps.tasks.models import TaskLog, Error
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings, LastExportDetail
from tests.helper import dict_compare_keys
from tests.test_fyle.fixtures import data


@pytest.mark.django_db()
def test_create_expense_groups(mocker, db):
    mock_call = mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expenses'])

    task_log, _ = TaskLog.objects.update_or_create(workspace_id=3, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=3)
    expense_group_settings.reimbursable_export_date_type = 'last_spent_at'
    expense_group_settings.ccc_export_date_type = 'last_spent_at'
    expense_group_settings.import_card_credits = True
    expense_group_settings.save()

    create_expense_groups(3, ['PERSONAL', 'CCC'], task_log)

    assert task_log.status == 'COMPLETE'

    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform.side_effect = RetryException('Retry Exception')
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log)

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

    mock_call.side_effect = InternalServerError('Error')
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log)

    mock_call.side_effect = InvalidTokenError('Invalid Token')
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log)

    mock_call.call_count = 2


@pytest.mark.django_db()
def test_create_expense_group_skipped_flow(mocker, api_client, test_connection):
    # Mock the re_run_skip_export_rule function
    mocker.patch('apps.fyle.signals.re_run_skip_export_rule', return_value=None)

    access_token = test_connection.access_token
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
    post_accounting_export_summary('or79Cob97KSh', 3, [expense_id])

    assert Expense.objects.filter(id=expense_id).first().accounting_export_summary['synced'] == True


def test_import_and_export_expenses(db, mocker):
    import_and_export_expenses('rp1s1L3QtMpF', 'or79Cob97KSh')

    mock_call = mocker.patch('apps.fyle.helpers.get_fund_source')
    mock_call.side_effect = WorkspaceGeneralSettings.DoesNotExist('Error')
    import_and_export_expenses('rp1s1L3QtMpF', 'or79Cob97KSh')

    assert mock_call.call_count == 0


def test_sync_dimension(db, mocker):
    mock_platform_connector = mocker.patch('apps.fyle.tasks.PlatformConnector')

    mock_platform_instance = mock_platform_connector.return_value
    mocker.patch.object(mock_platform_instance.categories, 'sync', return_value=None)
    mock_platform_instance.categories.get_count.return_value = 5
    mock_platform_instance.projects.get_count.return_value = 10

    fyle_creds = FyleCredential.objects.filter(workspace_id = 1).first()

    sync_dimensions(fyle_credentials=fyle_creds, is_export=True)

    mock_platform_instance.import_fyle_dimensions.assert_called_once_with(is_export=True)
    mock_platform_instance.categories.sync.assert_called_once()
    mock_platform_instance.projects.sync.assert_called_once()


def test_update_non_exported_expenses(db, create_temp_workspace, mocker, api_client, test_connection):
    expense = data['raw_expense']
    default_raw_expense = data['default_raw_expense']
    org_id = expense['org_id']
    payload = {
        "resource": "EXPENSE",
        "action": 'UPDATED_AFTER_APPROVAL',
        "data": expense,
        "reason": 'expense update testing',
    }

    # Create initial expense with is_skipped=True
    expense_created, _ = Expense.objects.update_or_create(
        org_id=org_id,
        expense_id='txhJLOSKs1iN',
        workspace_id=1,
        defaults={
            **default_raw_expense,
            'is_skipped': True  # Set initial skipped status
        }
    )
    expense_created.accounting_export_summary = {}
    expense_created.save()

    workspace = Workspace.objects.filter(id=1).first()
    workspace.fyle_org_id = org_id
    workspace.save()

    assert expense_created.category == 'Old Category'
    assert expense_created.is_skipped == True  # Verify initial skipped status

    # Test update of non-exported expense
    update_non_exported_expenses(payload['data'])

    expense = Expense.objects.get(expense_id='txhJLOSKs1iN', org_id=org_id)
    assert expense.category == 'ABN Withholding'
    assert expense.is_skipped == True  # Verify skipped status is preserved

    # Test that expense in COMPLETE state is not updated
    expense.accounting_export_summary = {"synced": True, "state": "COMPLETE"}
    expense.category = 'Old Category'
    expense.save()

    update_non_exported_expenses(payload['data'])
    expense = Expense.objects.get(expense_id='txhJLOSKs1iN', org_id=org_id)
    assert expense.category == 'Old Category'

    # Test expense in IN_PROGRESS state is not updated
    expense.accounting_export_summary = {"synced": True, "state": "IN_PROGRESS"}
    expense.save()

    update_non_exported_expenses(payload['data'])
    expense = Expense.objects.get(expense_id='txhJLOSKs1iN', org_id=org_id)
    assert expense.category == 'Old Category'

    try:
        update_non_exported_expenses(payload['data'])
    except ValidationError as e:
        assert e.detail[0] == 'Workspace mismatch'

    url = reverse('exports', kwargs={'workspace_id': 1})
    response = api_client.post(url, data=payload, format='json')
    assert response.status_code == status.HTTP_200_OK

    url = reverse('exports', kwargs={'workspace_id': 2})
    response = api_client.post(url, data=payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_re_run_skip_export_rule(db, create_temp_workspace, mocker, api_client, test_connection):
    """Test the re-running of skip export rules for expenses

    This test verifies that expenses are correctly skipped based on email filters,
    expense groups are properly cleaned up, and export details are updated.
    """
    # Create an expense filter that will match expenses with employee_email 'jhonsnow@fyle.in'
    ExpenseFilter.objects.create(
        workspace_id=1,
        condition='expense_number',
        operator='in',
        values=['expense_1'],
        rank=1,
        join_by=None,
    )

    # Retrieve test expenses data and modify them to ensure unique grouping
    expenses = list(data["expenses_spent_at"])
    expenses[0].update({
        'expense_number': 'expense_1',
        'employee_email': 'jhonsnow@fyle.in',
        'report_id': 'report_1',
        'claim_number': 'claim_1',
        'fund_source': 'PERSONAL'
    })
    expenses[1].update({
        'expense_number': 'expense_2',
        'employee_email': 'other.email@fyle.in',
        'report_id': 'report_2',
        'claim_number': 'claim_2',
        'fund_source': 'PERSONAL'
    })
    expenses[2].update({
        'expense_number': 'expense_3',
        'employee_email': 'anish@fyle.in',
        'report_id': 'report_3',
        'claim_number': 'claim_3',
        'fund_source': 'PERSONAL'
    })
    # Assign org_id to all expenses
    for expense in expenses:
        expense['org_id'] = 'orHVw3ikkCxJ'

    # Create expense objects in the database
    expense_objects = Expense.create_expense_objects(expenses, 1)

    # Mark all expenses as failed exports by updating their accounting_export_summary
    for expense in Expense.objects.filter(workspace_id=1):
        expense.accounting_export_summary = {
            'state': 'FAILED',
            'synced': False
        }
        expense.save()

    # Create expense groups - this should create 3 separate groups, one for each expense
    ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, 1)
    expense_groups = ExpenseGroup.objects.filter(workspace_id=1)

    expense_group_ids = expense_groups.values_list('id', flat=True)

    # Create LastExportDetail to simulate failed exports
    LastExportDetail.objects.create(
        workspace_id=1,
        total_expense_groups_count=len(expense_group_ids),  # 2 groups
        failed_expense_groups_count=1,  # Mark one group as failed
        export_mode='MANUAL'
    )

    # Create TaskLog to simulate in-progress export
    # get the first expense group id, and create a task log for it
    tasklog = TaskLog.objects.create(
        workspace_id=1,
        type='CREATING_BILL',
        status='FAILED',
        expense_group_id=expense_group_ids[0]
    )

    # Create error for the first expense group
    error = Error.objects.create(
        workspace_id=1,
        type='QBO_ERROR',
        error_title='Test error title',
        error_detail='Test error detail',
        expense_group=ExpenseGroup.objects.get(id=expense_group_ids[0])
    )

    workspace = Workspace.objects.get(id=1)

    assert tasklog.status == 'FAILED'
    assert error.type == 'QBO_ERROR'

    re_run_skip_export_rule(workspace)

    # Test 1: Verify expense skipping based on email filter
    skipped_expense = Expense.objects.get(expense_number='expense_1')
    non_skipped_expense = Expense.objects.get(expense_number='expense_2')
    assert skipped_expense.is_skipped == True
    assert non_skipped_expense.is_skipped == False

    # Test 2: Verify expense group modifications
    remaining_groups = ExpenseGroup.objects.filter(id__in=expense_group_ids)
    assert remaining_groups.count() == 1

    # Test 3: Verify cleanup of task logs
    task_log = TaskLog.objects.filter(workspace_id=1).first()
    assert task_log is None

    # Test 4: Verify cleanup of errors
    error = Error.objects.filter(workspace_id=1, expense_group_id__in=expense_group_ids).first()
    assert error is None

    # Test 5: Verify LastExportDetail updates
    last_export_detail = LastExportDetail.objects.filter(workspace_id=1).first()
    assert last_export_detail.failed_expense_groups_count == 0
