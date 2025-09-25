import json
from unittest import mock

import pytest
from django.db.models import Q
from django.urls import reverse
from django_q.models import Schedule
from fyle.platform.exceptions import InternalServerError, InvalidTokenError, RetryException
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.fyle.actions import mark_expenses_as_skipped
from apps.fyle.models import Expense, ExpenseFilter, ExpenseGroup, ExpenseGroupSettings
from apps.fyle.tasks import (
    cleanup_scheduled_task,
    construct_filter_for_affected_expense_groups,
    create_expense_groups,
    delete_expense_group_and_related_data,
    delete_expenses_in_db,
    group_expenses_and_save,
    handle_expense_fund_source_change,
    handle_fund_source_changes_for_expense_ids,
    import_and_export_expenses,
    post_accounting_export_summary,
    process_expense_group_for_fund_source_update,
    recreate_expense_groups,
    re_run_skip_export_rule,
    schedule_expense_group_creation,
    schedule_task_for_expense_group_fund_source_change,
    skip_expenses_and_post_accounting_export_summary,
    sync_dimensions,
    update_non_exported_expenses,
)
from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import FyleCredential, LastExportDetail, Workspace, WorkspaceGeneralSettings
from tests.helper import dict_compare_keys
from tests.test_fyle.fixtures import data


@pytest.mark.django_db()
def test_create_expense_groups(mocker, db):
    mock_call = mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expenses'])

    task_log, _ = TaskLog.objects.update_or_create(workspace_id=1, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=1)
    expense_group_settings.reimbursable_export_date_type = 'last_spent_at'
    expense_group_settings.ccc_export_date_type = 'last_spent_at'
    expense_group_settings.import_card_credits = True
    expense_group_settings.save()

    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    assert task_log.status == 'COMPLETE'

    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform.side_effect = RetryException('Retry Exception')
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    fyle_credential = FyleCredential.objects.get(workspace_id=1)
    fyle_credential.delete()
    task_log, _ = TaskLog.objects.update_or_create(workspace_id=1, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    task_log = TaskLog.objects.get(workspace_id=1)
    assert task_log.status == 'FAILED'

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=1)
    expense_group_settings.delete()

    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    task_log = TaskLog.objects.get(workspace_id=1)
    assert task_log.status == 'FATAL'

    mock_call.side_effect = InternalServerError('Error')
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    mock_call.side_effect = InvalidTokenError('Invalid Token')
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

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

        create_expense_groups(1, ['PERSONAL', 'CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)
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
    post_accounting_export_summary(3, [expense_id])

    assert Expense.objects.filter(id=expense_id).first().accounting_export_summary['synced'] == True


def test_import_and_export_expenses(db, mocker):
    import_and_export_expenses('rp1s1L3QtMpF', 'or79Cob97KSh', False, None, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    mock_call = mocker.patch('apps.fyle.helpers.get_fund_source')
    mock_call.side_effect = WorkspaceGeneralSettings.DoesNotExist('Error')
    import_and_export_expenses('rp1s1L3QtMpF', 'or79Cob97KSh', False, None, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    import_and_export_expenses('rp1s1L3QtMpF', 'orPJvXuoLqvJ', True, report_state='APPROVED', imported_from=ExpenseImportSourceEnum.WEBHOOK)
    assert mock_call.call_count == 0


def test_sync_dimension(db, mocker):
    mock_platform_connector = mocker.patch('apps.fyle.tasks.PlatformConnector')

    mock_platform_instance = mock_platform_connector.return_value
    mocker.patch.object(mock_platform_instance.categories, 'sync', return_value=None)
    mock_platform_instance.categories.get_count.return_value = 5
    mock_platform_instance.projects.get_count.return_value = 10

    sync_dimensions(1, is_export=True)

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
        'fund_source': 'PERSONAL',
        'amount': 1000
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
    expense_group_skipped = ExpenseGroup.objects.filter(workspace_id=1, expenses__expense_id=expenses[0]['id']).first()

    # Create TaskLog to simulate in-progress export
    # get the first expense group id, and create a task log for it
    tasklog = TaskLog.objects.create(
        workspace_id=1,
        type='CREATING_BILL',
        status='FAILED',
        expense_group_id=expense_group_skipped.id
    )

    # Create error for the first expense group
    error = Error.objects.create(
        workspace_id=1,
        type='QBO_ERROR',
        error_title='Test error title',
        error_detail='Test error detail',
        expense_group=ExpenseGroup.objects.get(id=expense_group_skipped.id)
    )

    LastExportDetail.objects.update_or_create(
        workspace_id=1,
        defaults={
            'total_expense_groups_count': len(expense_groups),
            'failed_expense_groups_count': 1,
            'export_mode': 'MANUAL'
        }
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
    assert remaining_groups.count() == 2

    # Test 3: Verify cleanup of task logs
    task_log = TaskLog.objects.filter(workspace_id=1).first()
    assert task_log is None

    # Test 4: Verify cleanup of errors
    error = Error.objects.filter(workspace_id=1, expense_group_id__in=expense_group_ids).first()
    assert error is None

    # Test 5: Verify LastExportDetail updates
    last_export_detail = LastExportDetail.objects.filter(workspace_id=1).first()
    assert last_export_detail.failed_expense_groups_count == 0


def test_import_and_export_expenses_direct_export_case_1(mocker, db, test_connection):
    """
    Test import and export expenses
    Case 1: Reimbursable expenses are not configured
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    configuration.reimbursable_expenses_object = None
    configuration.save()

    mock_call = mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.get',
        return_value=data['expenses_webhook']
    )

    mock_skip_expenses_and_post_accounting_export_summary = mocker.patch(
        'apps.fyle.tasks.skip_expenses_and_post_accounting_export_summary',
        return_value=None
    )

    import_and_export_expenses(
        report_id='rp1s1L3QtMpF',
        org_id=workspace.fyle_org_id,
        is_state_change_event=False,
        imported_from=ExpenseImportSourceEnum.DIRECT_EXPORT
    )

    assert mock_call.call_count == 1
    assert mock_skip_expenses_and_post_accounting_export_summary.call_count == 1


def test_import_and_export_expenses_direct_export_case_2(mocker, db, test_connection):
    """
    Test import and export expenses
    Case 2: Corporate credit card expenses are not configured
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    configuration.corporate_credit_card_expenses_object = None
    configuration.save()

    expense_data = data['expenses_webhook'].copy()
    expense_data[0]['org_id'] = workspace.fyle_org_id
    expense_data[0]['source_account_type'] = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'

    mock_call = mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.get',
        return_value=expense_data
    )

    mock_skip_expenses_and_post_accounting_export_summary = mocker.patch(
        'apps.fyle.tasks.skip_expenses_and_post_accounting_export_summary',
        return_value=None
    )

    import_and_export_expenses(
        report_id='rp1s1L3QtMpF',
        org_id=workspace.fyle_org_id,
        is_state_change_event=False,
        imported_from=ExpenseImportSourceEnum.DIRECT_EXPORT
    )

    assert mock_call.call_count == 1
    assert mock_skip_expenses_and_post_accounting_export_summary.call_count == 1


def test_import_and_export_expenses_direct_export_case_3(mocker, db, test_connection):
    """
    Test import and export expenses
    Case 3: Negative expesnes with filter_credit_expenses=True
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    configuration.corporate_credit_card_expenses_object = None
    configuration.save()

    expense_data = data['expenses_webhook'].copy()
    expense_data[0]['org_id'] = workspace.fyle_org_id
    expense_data[0]['source_account_type'] = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'
    expense_data[0]['amount'] = -100

    mock_call = mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.get',
        return_value=expense_data
    )

    mock_skip_expenses_and_post_accounting_export_summary = mocker.patch(
        'apps.fyle.tasks.skip_expenses_and_post_accounting_export_summary',
        return_value=None
    )

    import_and_export_expenses(
        report_id='rp1s1L3QtMpF',
        org_id=workspace.fyle_org_id,
        is_state_change_event=False,
        imported_from=ExpenseImportSourceEnum.DIRECT_EXPORT
    )

    assert mock_call.call_count == 1
    assert mock_skip_expenses_and_post_accounting_export_summary.call_count == 1


def test_skip_expenses_and_post_accounting_export_summary(mocker, db):
    """
    Test skip expenses and post accounting export summary
    """
    workspace = Workspace.objects.get(id=1)

    expense = Expense.objects.filter(org_id='or79Cob97KSh').first()
    expense.workspace = workspace
    expense.org_id = workspace.fyle_org_id
    expense.accounting_export_summary = {}
    expense.is_skipped = False
    expense.fund_source = 'PERSONAL'
    expense.save()

    # Patch mark_expenses_as_skipped to return the expense in a list
    mock_mark_skipped = mocker.patch(
        'apps.fyle.tasks.mark_expenses_as_skipped',
        return_value=[expense]
    )
    # Patch post_accounting_export_summary to just record the call
    mock_post_summary = mocker.patch(
        'apps.fyle.tasks.post_accounting_export_summary',
        return_value=None
    )

    skip_expenses_and_post_accounting_export_summary([expense.id], workspace)

    # Assert mark_expenses_as_skipped was called with Q(), [expense.id], workspace
    assert mock_mark_skipped.call_count == 1
    args, _ = mock_mark_skipped.call_args
    assert args[1] == [expense.id]
    assert args[2] == workspace

    # Assert post_accounting_export_summary was called with workspace_id and expense_ids
    assert mock_post_summary.call_count == 1
    _, post_kwargs = mock_post_summary.call_args
    assert post_kwargs['workspace_id'] == workspace.id
    assert post_kwargs['expense_ids'] == [expense.id]


@pytest.mark.django_db()
def test_schedule_expense_group_creation(mocker, db):
    """
    Test schedule expense group creation
    """
    workspace_id = 1

    mock_async_task = mocker.patch(
        'apps.fyle.tasks.async_task',
        return_value=None
    )

    schedule_expense_group_creation(workspace_id=workspace_id)

    assert mock_async_task.call_count == 1
    args, _ = mock_async_task.call_args
    assert args[0] == 'apps.fyle.tasks.create_expense_groups'
    assert args[1] == workspace_id


@pytest.mark.django_db()
def test_skip_expenses_and_post_accounting_export_summary_with_q_filters(mocker, db):
    """
    Test skip expenses and post accounting export summary with Q filters
    """
    workspace = Workspace.objects.get(id=1)
    expense = Expense.objects.filter(org_id='or79Cob97KSh').first()

    mock_mark_skipped = mocker.patch(
        'apps.fyle.tasks.mark_expenses_as_skipped',
        return_value=[expense]
    )
    mocker.patch(
        'apps.fyle.tasks.post_accounting_export_summary',
        return_value=None
    )

    q_filters = Q(category='Test Category')
    skip_expenses_and_post_accounting_export_summary([expense.id], workspace, q_filters)

    assert mock_mark_skipped.call_count == 1
    args, _ = mock_mark_skipped.call_args
    assert args[0] == q_filters
    assert args[1] == [expense.id]
    assert args[2] == workspace


@pytest.mark.django_db()
def test_handle_fund_source_changes_for_expense_ids(mocker, db):
    """
    Test handle fund source changes for expense ids
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.filter(workspace_id=workspace_id).first()
    expense = expense_group.expenses.first()
    changed_expense_ids = [expense.id]
    report_id = expense.report_id

    handle_fund_source_changes_for_expense_ids(
        workspace_id=workspace_id,
        changed_expense_ids=changed_expense_ids,
        report_id=report_id,
        affected_fund_source_expense_ids={'PERSONAL': changed_expense_ids, 'CCC': []},
        task_name='test_task'
    )


@pytest.mark.django_db()
def test_process_expense_group_for_fund_source_update_enqueued_status(mocker, db):
    """
    Test process expense group when task log is ENQUEUED
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.filter(workspace_id=workspace_id).first()
    changed_expense_ids = [expense_group.expenses.first().id]

    task_log, _ = TaskLog.objects.get_or_create(
        expense_group_id=expense_group.id,
        defaults={
            'workspace_id': workspace_id,
            'type': 'CREATING_BILL',
            'status': 'ENQUEUED'
        }
    )
    task_log.status = 'ENQUEUED'
    task_log.save()

    mock_schedule = mocker.patch(
        'apps.fyle.tasks.schedule_task_for_expense_group_fund_source_change',
        return_value=None
    )

    result = process_expense_group_for_fund_source_update(
        expense_group=expense_group,
        changed_expense_ids=changed_expense_ids,
        workspace_id=workspace_id,
        report_id='rp1s1L3QtMpF',
        affected_fund_source_expense_ids={'PERSONAL': changed_expense_ids}
    )

    assert result is False
    assert mock_schedule.call_count == 1
    task_log.delete()


@pytest.mark.django_db()
def test_process_expense_group_for_fund_source_update_in_progress_status(mocker, db):
    """
    Test process expense group when task log is IN_PROGRESS
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.filter(workspace_id=workspace_id).first()
    changed_expense_ids = [expense_group.expenses.first().id]

    TaskLog.objects.filter(expense_group_id=expense_group.id).delete()

    task_log = TaskLog.objects.create(
        workspace_id=workspace_id,
        type='CREATING_BILL',
        expense_group_id=expense_group.id,
        status='IN_PROGRESS'
    )

    mock_schedule = mocker.patch(
        'apps.fyle.tasks.schedule_task_for_expense_group_fund_source_change',
        return_value=None
    )

    result = process_expense_group_for_fund_source_update(
        expense_group=expense_group,
        changed_expense_ids=changed_expense_ids,
        workspace_id=workspace_id,
        report_id='rp1s1L3QtMpF',
        affected_fund_source_expense_ids={'PERSONAL': changed_expense_ids}
    )

    assert result is False
    assert mock_schedule.call_count == 1
    task_log.delete()


@pytest.mark.django_db()
def test_process_expense_group_for_fund_source_update_complete_status(mocker, db):
    """
    Test process expense group when task log is COMPLETE
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.filter(workspace_id=workspace_id).first()
    changed_expense_ids = [expense_group.expenses.first().id]

    TaskLog.objects.filter(expense_group_id=expense_group.id).delete()

    task_log = TaskLog.objects.create(
        workspace_id=workspace_id,
        type='CREATING_BILL',
        expense_group_id=expense_group.id,
        status='COMPLETE'
    )

    mock_delete_recreate = mocker.patch(
        'apps.fyle.tasks.delete_expense_group_and_related_data',
        return_value=None
    )

    result = process_expense_group_for_fund_source_update(
        expense_group=expense_group,
        changed_expense_ids=changed_expense_ids,
        workspace_id=workspace_id,
        report_id='rp1s1L3QtMpF',
        affected_fund_source_expense_ids={'PERSONAL': changed_expense_ids}
    )

    assert result is False
    assert mock_delete_recreate.call_count == 0
    task_log.delete()


@pytest.mark.django_db()
def test_process_expense_group_for_fund_source_update_no_task_log(mocker, db):
    """
    Test process expense group when no task log exists
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.filter(workspace_id=workspace_id).first()
    changed_expense_ids = [expense_group.expenses.first().id]

    TaskLog.objects.filter(expense_group_id=expense_group.id).delete()

    mock_delete_recreate = mocker.patch(
        'apps.fyle.tasks.delete_expense_group_and_related_data',
        return_value=None
    )

    result = process_expense_group_for_fund_source_update(
        expense_group=expense_group,
        changed_expense_ids=changed_expense_ids,
        workspace_id=workspace_id,
        report_id='rp1s1L3QtMpF',
        affected_fund_source_expense_ids={'PERSONAL': changed_expense_ids}
    )

    assert result is True
    assert mock_delete_recreate.call_count == 1


@pytest.mark.django_db()
def test_delete_expense_group_and_related_data(mocker, db):
    """
    Test delete expense group and related data
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.filter(workspace_id=workspace_id).first()

    TaskLog.objects.filter(expense_group_id=expense_group.id).delete()

    task_log = TaskLog.objects.create(
        workspace_id=workspace_id,
        type='CREATING_BILL',
        expense_group_id=expense_group.id,
        status='FAILED'
    )

    error = Error.objects.create(
        workspace_id=workspace_id,
        expense_group_id=expense_group.id,
        type='QBO_ERROR'
    )

    error_with_mapping = Error.objects.create(
        workspace_id=workspace_id,
        type='MAPPING_ERROR',
        mapping_error_expense_group_ids=[expense_group.id, 999]
    )

    mock_expense_group_delete = mocker.patch.object(expense_group, 'delete')

    delete_expense_group_and_related_data(expense_group=expense_group, workspace_id=workspace_id)

    assert not TaskLog.objects.filter(id=task_log.id).exists()
    assert not Error.objects.filter(id=error.id).exists()

    error_with_mapping.refresh_from_db()
    assert expense_group.id not in error_with_mapping.mapping_error_expense_group_ids
    assert 999 in error_with_mapping.mapping_error_expense_group_ids

    mock_expense_group_delete.assert_called_once()
    error_with_mapping.delete()


@pytest.mark.django_db()
def test_schedule_task_for_expense_group_fund_source_change(mocker, db):
    """
    Test schedule task for expense group fund source change
    """
    workspace_id = 3  # Use workspace_id=3 which has expense groups in fixtures
    expense_group = ExpenseGroup.objects.filter(workspace_id=workspace_id).first()
    changed_expense_ids = [expense_group.expenses.first().id]

    mock_schedule = mocker.patch(
        'apps.fyle.tasks.schedule',
        return_value=None
    )

    schedule_task_for_expense_group_fund_source_change(
        changed_expense_ids=changed_expense_ids,
        workspace_id=workspace_id,
        report_id='rp1s1L3QtMpF',
        affected_fund_source_expense_ids={'PERSONAL': changed_expense_ids}
    )

    assert mock_schedule.call_count == 1
    args, _ = mock_schedule.call_args
    assert args[0] == 'apps.fyle.tasks.handle_fund_source_changes_for_expense_ids'
    assert args[1] == workspace_id
    assert args[2] == changed_expense_ids


@pytest.mark.django_db()
def test_schedule_task_existing_schedule(mocker, db):
    """
    Test schedule task when schedule already exists
    """
    import hashlib
    workspace_id = 3  # Use workspace_id=3 which has expense groups in fixtures
    expense_group = ExpenseGroup.objects.filter(workspace_id=workspace_id).first()
    changed_expense_ids = [expense_group.expenses.first().id]

    # Generate the same task name that the function will generate
    hashed_name = hashlib.md5(str(changed_expense_ids).encode('utf-8')).hexdigest()[0:6]
    task_name = f'fund_source_change_retry_{hashed_name}_{workspace_id}'

    existing_schedule = Schedule.objects.create(
        func='apps.fyle.tasks.handle_fund_source_changes_for_expense_ids',
        name=task_name,
        args='[]'
    )

    mock_schedule = mocker.patch(
        'apps.fyle.tasks.schedule',
        return_value=None
    )

    expense = expense_group.expenses.first()
    report_id = expense.report_id

    schedule_task_for_expense_group_fund_source_change(
        changed_expense_ids=changed_expense_ids,
        workspace_id=workspace_id,
        report_id=report_id,
        affected_fund_source_expense_ids={'PERSONAL': changed_expense_ids}
    )

    # Should not schedule a new task since one already exists
    assert mock_schedule.call_count == 0
    existing_schedule.delete()


@pytest.mark.django_db()
def test_cleanup_scheduled_task_exists(mocker, db):
    """
    Test cleanup scheduled task when task exists
    """
    workspace_id = 1
    task_name = 'test_task_name'

    schedule_obj = Schedule.objects.create(
        func='apps.fyle.tasks.handle_fund_source_changes_for_expense_ids',
        name=task_name,
        args='[]'
    )

    cleanup_scheduled_task(task_name=task_name, workspace_id=workspace_id)

    # Verify the scheduled task was deleted
    assert not Schedule.objects.filter(id=schedule_obj.id).exists()


@pytest.mark.django_db()
def test_cleanup_scheduled_task_not_exists(mocker, db):
    """
    Test cleanup scheduled task when task does not exist
    """
    workspace_id = 1
    task_name = 'non_existent_task'

    # This should not raise any exception
    cleanup_scheduled_task(task_name=task_name, workspace_id=workspace_id)


@pytest.mark.django_db()
def test_update_non_exported_expenses_fund_source_change(mocker, db):
    """
    Test update non exported expenses with fund source change
    """
    expense_data = data['raw_expense'].copy()
    expense_data['source_account_type'] = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'
    expense_data['custom_properties'] = {}  # Add missing field
    org_id = expense_data['org_id']

    default_raw_expense = data['default_raw_expense'].copy()
    default_raw_expense['fund_source'] = 'PERSONAL'  # Original fund source

    expense_created, _ = Expense.objects.update_or_create(
        org_id=org_id,
        expense_id='txhJLOSKs1iN',
        workspace_id=1,
        defaults=default_raw_expense
    )
    expense_created.accounting_export_summary = {}
    expense_created.save()

    workspace = Workspace.objects.filter(id=1).first()
    workspace.fyle_org_id = org_id
    workspace.save()

    # Mock the FyleExpenses construct_expense_object method
    mock_fyle_expenses = mocker.patch('apps.fyle.tasks.FyleExpenses')
    mock_fyle_expenses.return_value.construct_expense_object.return_value = [expense_data]

    # Mock create_expense_objects to avoid complex data structure requirements
    mocker.patch('apps.fyle.tasks.Expense.create_expense_objects', return_value=None)

    mock_handle_fund_source_changes = mocker.patch(
        'apps.fyle.tasks.handle_fund_source_changes_for_expense_ids',
        return_value=None
    )

    update_non_exported_expenses(expense_data)

    # Verify fund source change handling was called
    assert mock_handle_fund_source_changes.call_count == 1
    _, kwargs = mock_handle_fund_source_changes.call_args
    assert kwargs['workspace_id'] == expense_created.workspace_id
    assert kwargs['changed_expense_ids'] == [expense_created.id]
    assert kwargs['report_id'] == expense_created.report_id
    assert kwargs['affected_fund_source_expense_ids'] == {'PERSONAL': [expense_created.id]}


def test_group_expenses_and_save_with_skipped_expense_ids_exception(mocker, db):
    workspace = Workspace.objects.get(id=1)
    task_log = TaskLog.objects.create(workspace_id=workspace.id, type='FETCHING_EXPENSES', status='IN_PROGRESS')

    expenses = data['expenses'][:1]

    mocker.patch(
        'apps.fyle.models.ExpenseGroup.create_expense_groups_by_report_id_fund_source',
        return_value=([], [1, 2])
    )

    mock_expense = mocker.MagicMock()
    mock_expense.id = 1
    mock_mark_skipped = mocker.patch(
        'apps.fyle.tasks.mark_expenses_as_skipped',
        return_value=[mock_expense]
    )

    mock_post_summary = mocker.patch(
        'apps.fyle.tasks.post_accounting_export_summary',
        side_effect=Exception("Test exception")
    )

    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    group_expenses_and_save(
        expenses=expenses,
        task_log=task_log,
        workspace=workspace,
        imported_from=ExpenseImportSourceEnum.DASHBOARD_SYNC,
        filter_credit_expenses=False
    )

    assert mock_mark_skipped.call_count == 1
    assert mock_post_summary.call_count == 1
    assert mock_logger.error.call_count == 1
    mock_logger.error.assert_called_with('Error posting accounting export summary for workspace_id: %s', workspace.id)


def test_import_and_export_expenses_fund_source_change_exception(mocker, db):
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    report_id = 'rp1s1L3QtMpF'

    expense_data = data['expenses'][0].copy()
    expense_data['report_id'] = report_id
    expense_data['org_id'] = workspace.fyle_org_id
    Expense.create_expense_objects([expense_data], workspace_id)

    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform_instance = mock_platform.return_value
    mock_platform_instance.expenses.get.return_value = []

    mock_handle_fund_source = mocker.patch(
        'apps.fyle.tasks.handle_expense_fund_source_change',
        side_effect=Exception("Fund source change error")
    )

    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    import_and_export_expenses(
        report_id=report_id,
        org_id=workspace.fyle_org_id,
        is_state_change_event=False,
        report_state='APPROVED',
        imported_from=ExpenseImportSourceEnum.DASHBOARD_SYNC
    )

    assert mock_handle_fund_source.call_count == 1
    assert mock_logger.exception.call_count == 1
    mock_logger.exception.assert_called_with(
        "Error handling expense fund source change for workspace_id: %s, report_id: %s | ERROR: %s",
        workspace.id, report_id, mock_handle_fund_source.side_effect
    )


def test_handle_expense_fund_source_change_complete_flow(mocker, db):
    workspace_id = 1
    report_id = 'rp1s1L3QtMpF'

    expense_data_1 = data['expenses'][0].copy()
    expense_data_1['id'] = 'tx1'
    expense_data_1['report_id'] = report_id
    expense_data_1['source_account_type'] = 'PERSONAL_CASH_ACCOUNT'

    expense_data_2 = data['expenses'][0].copy()
    expense_data_2['id'] = 'tx2'
    expense_data_2['report_id'] = report_id
    expense_data_2['source_account_type'] = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'

    Expense.create_expense_objects([expense_data_1, expense_data_2], workspace_id)

    mock_expenses = [
        {
            'id': 'tx1',
            'source_account_type': 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'
        },
        {
            'id': 'tx2',
            'source_account_type': 'PERSONAL_CASH_ACCOUNT'
        }
    ]

    mock_platform = mocker.MagicMock()
    mock_platform.expenses.get.return_value = mock_expenses

    mock_create_objects = mocker.patch('apps.fyle.tasks.Expense.create_expense_objects')
    mock_handle_changes = mocker.patch('apps.fyle.tasks.handle_fund_source_changes_for_expense_ids')
    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    handle_expense_fund_source_change(workspace_id, report_id, mock_platform)

    mock_platform.expenses.get.assert_called_once_with(
        source_account_type=['PERSONAL_CASH_ACCOUNT', 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'],
        report_id=report_id,
        filter_credit_expenses=False
    )

    assert mock_logger.info.call_count >= 2
    assert mock_create_objects.call_count == 1
    assert mock_handle_changes.call_count == 1


def test_handle_fund_source_changes_no_affected_groups(mocker, db):
    workspace_id = 3
    changed_expense_ids = [999]
    report_id = 'rp1s1L3QtMpF'
    affected_fund_source_expense_ids = {'PERSONAL': [999]}

    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    mocker.patch(
        'apps.fyle.tasks.construct_filter_for_affected_expense_groups',
        return_value=Q(id__in=[999])
    )

    handle_fund_source_changes_for_expense_ids(
        workspace_id=workspace_id,
        changed_expense_ids=changed_expense_ids,
        report_id=report_id,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    mock_logger.info.assert_called_with(
        "No expense groups found for changed expenses: %s in workspace %s",
        changed_expense_ids, workspace_id
    )


def test_recreate_expense_groups_no_expenses_found(mocker, db):

    workspace_id = 1
    expense_ids = [999]

    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    recreate_expense_groups(workspace_id=workspace_id, expense_ids=expense_ids)

    mock_logger.warning.assert_called_with(
        "No expenses found for recreation: %s in workspace %s", expense_ids, workspace_id
    )


def test_recreate_expense_groups_no_reimbursable_config(mocker, db):

    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    expense_data = data['expenses'][0].copy()
    expense_data['org_id'] = workspace.fyle_org_id
    expense_data['source_account_type'] = 'PERSONAL_CASH_ACCOUNT'
    expense_objects = Expense.create_expense_objects([expense_data], workspace_id)
    expense_ids = [obj.id for obj in expense_objects]

    config = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    config.reimbursable_expenses_object = None
    config.save()

    recreate_expense_groups(workspace_id=workspace_id, expense_ids=expense_ids)

    remaining_expenses = Expense.objects.filter(id__in=expense_ids, workspace_id=workspace_id)
    assert remaining_expenses.count() == 0


def test_recreate_expense_groups_no_ccc_config(mocker, db):

    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    expense_data = data['expenses'][0].copy()
    expense_data['org_id'] = workspace.fyle_org_id
    expense_data['source_account_type'] = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'
    expense_objects = Expense.create_expense_objects([expense_data], workspace_id)
    expense_ids = [obj.id for obj in expense_objects]

    config = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    config.corporate_credit_card_expenses_object = None
    config.save()

    recreate_expense_groups(workspace_id=workspace_id, expense_ids=expense_ids)

    remaining_expenses = Expense.objects.filter(id__in=expense_ids, workspace_id=workspace_id)
    assert remaining_expenses.count() == 0


def test_delete_expenses_in_db(mocker, db):
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    expense_data = data['expenses'][:2]
    for expense in expense_data:
        expense['org_id'] = workspace.fyle_org_id

    expense_objects = Expense.create_expense_objects(expense_data, workspace_id)
    expense_ids = [obj.id for obj in expense_objects]

    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    delete_expenses_in_db(expense_ids=expense_ids, workspace_id=workspace_id)

    assert not Expense.objects.filter(id__in=expense_ids).exists()
    mock_logger.info.assert_called_with("Deleted %s expenses in workspace %s", len(expense_ids), workspace_id)


def test_construct_filter_both_report_grouping(mocker, db):
    workspace_id = 1
    report_id = 'rp1s1L3QtMpF'
    changed_expense_ids = [1, 2]
    affected_fund_source_expense_ids = {'PERSONAL': [1], 'CCC': [2]}

    mocker.patch(
        'apps.fyle.tasks.get_grouping_types',
        return_value={'PERSONAL': 'report', 'CCC': 'report'}
    )

    result = construct_filter_for_affected_expense_groups(
        workspace_id=workspace_id,
        report_id=report_id,
        changed_expense_ids=changed_expense_ids,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    assert 'expenses__report_id' in str(result)


def test_construct_filter_both_expense_grouping(mocker, db):
    workspace_id = 1
    report_id = 'rp1s1L3QtMpF'
    changed_expense_ids = [1, 2]
    affected_fund_source_expense_ids = {'PERSONAL': [1], 'CCC': [2]}

    mocker.patch(
        'apps.fyle.tasks.get_grouping_types',
        return_value={'PERSONAL': 'expense', 'CCC': 'expense'}
    )

    result = construct_filter_for_affected_expense_groups(
        workspace_id=workspace_id,
        report_id=report_id,
        changed_expense_ids=changed_expense_ids,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    assert 'expenses__id__in' in str(result)


def test_construct_filter_mixed_grouping_personal_report_ccc_expense(mocker, db):
    workspace_id = 1
    report_id = 'rp1s1L3QtMpF'
    changed_expense_ids = [1, 2]
    affected_fund_source_expense_ids = {'PERSONAL': [1], 'CCC': [2]}

    mocker.patch(
        'apps.fyle.tasks.get_grouping_types',
        return_value={'PERSONAL': 'report', 'CCC': 'expense'}
    )

    result = construct_filter_for_affected_expense_groups(
        workspace_id=workspace_id,
        report_id=report_id,
        changed_expense_ids=changed_expense_ids,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    result_str = str(result)
    assert 'expenses__report_id' in result_str
    assert 'expenses__id__in' in result_str


def test_construct_filter_mixed_grouping_personal_expense_ccc_report(mocker, db):
    workspace_id = 1
    report_id = 'rp1s1L3QtMpF'
    changed_expense_ids = [1, 2]
    affected_fund_source_expense_ids = {'PERSONAL': [1], 'CCC': [2]}

    mocker.patch(
        'apps.fyle.tasks.get_grouping_types',
        return_value={'PERSONAL': 'expense', 'CCC': 'report'}
    )

    result = construct_filter_for_affected_expense_groups(
        workspace_id=workspace_id,
        report_id=report_id,
        changed_expense_ids=changed_expense_ids,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    result_str = str(result)
    assert 'expenses__report_id' in result_str
    assert 'expenses__id__in' in result_str


def test_skip_expenses_and_post_accounting_export_summary_exception(mocker, db):
    workspace = Workspace.objects.get(id=1)
    expense_ids = [1, 2]

    mocker.patch(
        'apps.fyle.tasks.mark_expenses_as_skipped',
        return_value=[mocker.MagicMock(id=1)]
    )
    mocker.patch(
        'apps.fyle.tasks.post_accounting_export_summary',
        side_effect=Exception("Test exception")
    )
    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    skip_expenses_and_post_accounting_export_summary(expense_ids, workspace)

    mock_logger.exception.assert_called_with('Error posting accounting export summary for workspace_id: %s', workspace.id)


def test_group_expenses_and_save_with_expense_filters_exception(mocker, db):
    workspace = Workspace.objects.get(id=1)
    task_log = TaskLog.objects.create(workspace_id=workspace.id, type='FETCHING_EXPENSES', status='IN_PROGRESS')
    expenses = data['expenses'][:1]

    ExpenseFilter.objects.create(
        workspace_id=workspace.id,
        condition='category',
        operator='in',
        values=['Test'],
        rank=1
    )

    mock_expense = mocker.MagicMock()
    mock_expense.id = 1
    mocker.patch(
        'apps.fyle.tasks.mark_expenses_as_skipped',
        return_value=[mock_expense]
    )
    mocker.patch(
        'apps.fyle.tasks.post_accounting_export_summary',
        side_effect=Exception("Test exception")
    )
    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    group_expenses_and_save(
        expenses=expenses,
        task_log=task_log,
        workspace=workspace,
        imported_from=ExpenseImportSourceEnum.DASHBOARD_SYNC,
        filter_credit_expenses=False
    )

    mock_logger.error.assert_called_with('Error posting accounting export summary for workspace_id: %s', workspace.id)


def test_create_expense_groups_paid_state(mocker, db):
    workspace_id = 1

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.expense_state = 'PAID'
    expense_group_settings.save()

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=[])

    task_log = TaskLog.objects.create(workspace_id=workspace_id, type='FETCHING_EXPENSES', status='IN_PROGRESS')

    create_expense_groups(workspace_id, ['PERSONAL'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    assert task_log.status == 'COMPLETE'


def test_create_expense_groups_ccc_payment_processing_state(mocker, db):
    workspace_id = 1

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.ccc_expense_state = 'PAYMENT_PROCESSING'
    expense_group_settings.save()

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=[])

    task_log = TaskLog.objects.create(workspace_id=workspace_id, type='FETCHING_EXPENSES', status='IN_PROGRESS')

    create_expense_groups(workspace_id, ['CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    assert task_log.status == 'COMPLETE'


def test_create_expense_groups_ccc_approved_state(mocker, db):
    workspace_id = 1

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.ccc_expense_state = 'APPROVED'
    expense_group_settings.save()

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=[])

    task_log = TaskLog.objects.create(workspace_id=workspace_id, type='FETCHING_EXPENSES', status='IN_PROGRESS')

    create_expense_groups(workspace_id, ['CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    assert task_log.status == 'COMPLETE'


def test_create_expense_groups_invalid_token_error(mocker, db):
    workspace_id = 1

    mocker.patch('apps.fyle.tasks.PlatformConnector', side_effect=InvalidTokenError('Invalid token'))
    mock_update_task_log = mocker.patch('apps.fyle.tasks.update_task_log_post_import')
    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    task_log = TaskLog.objects.create(workspace_id=workspace_id, type='FETCHING_EXPENSES', status='IN_PROGRESS')

    create_expense_groups(workspace_id, ['PERSONAL'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    mock_logger.info.assert_called_with("Invalid Token for Fyle")
    mock_update_task_log.assert_called_with(task_log, 'FAILED', "Invalid Fyle credentials")


def test_import_and_export_expenses_state_change_filter(mocker, db):
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    report_id = 'rp1s1L3QtMpF'

    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform_instance = mock_platform.return_value
    mock_platform_instance.expenses.get.return_value = data['expenses'][:1]

    mocker.patch('apps.fyle.tasks.filter_expenses_based_on_state', return_value=data['expenses'][:1])

    import_and_export_expenses(
        report_id=report_id,
        org_id=workspace.fyle_org_id,
        is_state_change_event=True,
        report_state='APPROVED',
        imported_from=ExpenseImportSourceEnum.WEBHOOK
    )


def test_import_and_export_expenses_workspace_general_settings_not_found(mocker, db):
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    report_id = 'rp1s1L3QtMpF'

    mocker.patch('apps.workspaces.models.WorkspaceGeneralSettings.objects.get', side_effect=WorkspaceGeneralSettings.DoesNotExist())
    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    import_and_export_expenses(
        report_id=report_id,
        org_id=workspace.fyle_org_id,
        is_state_change_event=False,
        imported_from=ExpenseImportSourceEnum.DASHBOARD_SYNC
    )

    mock_logger.info.assert_called_with('Workspace general settings not found %s', workspace.id)

    task_log = TaskLog.objects.filter(workspace_id=workspace_id, type='FETCHING_EXPENSES').first()
    assert task_log.status == 'FAILED'
    assert task_log.detail == {'message': 'Workspace general settings do not exist in workspace'}


def test_import_and_export_expenses_general_exception(mocker, db):
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    report_id = 'rp1s1L3QtMpF'

    mocker.patch('apps.fyle.helpers.get_fund_source', side_effect=Exception('General error'))
    mock_handle_import_exception = mocker.patch('apps.fyle.tasks.handle_import_exception')

    import_and_export_expenses(
        report_id=report_id,
        org_id=workspace.fyle_org_id,
        is_state_change_event=False,
        imported_from=ExpenseImportSourceEnum.DASHBOARD_SYNC
    )

    assert mock_handle_import_exception.call_count == 1


def test_re_run_skip_export_rule_exception_in_post_summary(mocker, db):
    workspace = Workspace.objects.get(id=1)

    ExpenseFilter.objects.create(
        workspace_id=workspace.id,
        condition='category',
        operator='in',
        values=['Test'],
        rank=1
    )

    Expense.objects.create(
        employee_email='test@example.com',
        employee_name='Test Employee',
        category='Test',
        sub_category='Sub Test',
        project='Test Project',
        expense_id='tx1234',
        expense_number='E/2023/01/T/1',
        claim_number='C/2023/01/R/1',
        amount=100.0,
        currency='USD',
        foreign_amount=100.0,
        foreign_currency='USD',
        settlement_id='settlement123',
        reimbursable=True,
        billable=False,
        state='APPROVED',
        vendor='Test Vendor',
        cost_center='Test Cost Center',
        purpose='Test Purpose',
        report_id='rp1234',
        spent_at='2023-01-01T00:00:00Z',
        approved_at='2023-01-01T00:00:00Z',
        expense_created_at='2023-01-01T00:00:00Z',
        expense_updated_at='2023-01-01T00:00:00Z',
        created_at='2023-01-01T00:00:00Z',
        updated_at='2023-01-01T00:00:00Z',
        fund_source='PERSONAL',
        verified_at='2023-01-01T00:00:00Z',
        custom_properties={},
        org_id=workspace.fyle_org_id,
        workspace_id=workspace.id,
        accounting_export_summary={}
    )

    mocker.patch(
        'apps.fyle.tasks.post_accounting_export_summary',
        side_effect=Exception("Post summary error")
    )
    mock_logger = mocker.patch('apps.fyle.tasks.logger')

    re_run_skip_export_rule(workspace)

    mock_logger.error.assert_called_with('Error posting accounting export summary for workspace_id: %s', workspace.id)
