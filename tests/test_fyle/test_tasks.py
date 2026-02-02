import json
from datetime import datetime, timezone
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
    _delete_expense_groups_for_report,
    _handle_expense_ejected_from_report,
    cleanup_scheduled_task,
    construct_filter_for_affected_expense_groups,
    create_expense_groups,
    delete_expense_group_and_related_data,
    delete_expenses_in_db,
    get_grouping_types,
    get_task_log_and_fund_source,
    group_expenses_and_save,
    handle_category_changes_for_expense,
    handle_expense_fund_source_change,
    handle_expense_report_change,
    handle_fund_source_changes_for_expense_ids,
    handle_org_setting_updated,
    import_and_export_expenses,
    post_accounting_export_summary,
    process_expense_group_for_fund_source_update,
    re_run_skip_export_rule,
    recreate_expense_groups,
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

    # Mock FyleCredential
    mocker.patch('apps.fyle.tasks.FyleCredential.objects.get')

    # Mock the PlatformConnector and expenses.construct_expense_object method
    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    constructed_expense = expense_data.copy()
    constructed_expense['category'] = expense_data['category']['name']
    constructed_expense['sub_category'] = expense_data['category']['sub_category']
    mock_platform.return_value.expenses.construct_expense_object.return_value = [constructed_expense]

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

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
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

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
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

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
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

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
    workspace_id = 3
    changed_expense_ids = [999]
    report_id = 'rp1s1L3QtMpF'
    affected_fund_source_expense_ids = {'PERSONAL': [999]}

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
    mock_logger = mocker.patch('apps.fyle.tasks.logger')
    workspace_id = 1
    expense_ids = [999]

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

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    expense_data = data['expenses'][:2]
    for expense in expense_data:
        expense['org_id'] = workspace.fyle_org_id

    expense_objects = Expense.create_expense_objects(expense_data, workspace_id)
    expense_ids = [obj.id for obj in expense_objects]

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

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
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

    skip_expenses_and_post_accounting_export_summary(expense_ids, workspace)

    mock_logger.exception.assert_called_with('Error posting accounting export summary for workspace_id: %s', workspace.id)


def test_group_expenses_and_save_with_expense_filters_exception(mocker, db):

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
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

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
    workspace_id = 1

    mocker.patch('apps.fyle.tasks.PlatformConnector', side_effect=InvalidTokenError('Invalid token'))
    mock_update_task_log = mocker.patch('apps.fyle.tasks.update_task_log_post_import')

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

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    report_id = 'rp1s1L3QtMpF'

    mocker.patch('apps.workspaces.models.WorkspaceGeneralSettings.objects.get', side_effect=WorkspaceGeneralSettings.DoesNotExist())

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

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
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

    re_run_skip_export_rule(workspace)

    mock_logger.error.assert_called_with('Error posting accounting export summary for workspace_id: %s', workspace.id)


@pytest.mark.django_db()
def test_delete_expense_group_mapping_error_empty_list_deletion(mocker, db):
    """
    Test delete expense group when mapping error list becomes empty after removal
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.filter(workspace_id=workspace_id).first()

    # Create an error with only this expense group in mapping_error_expense_group_ids
    error_with_mapping = Error.objects.create(
        workspace_id=workspace_id,
        type='MAPPING_ERROR',
        mapping_error_expense_group_ids=[expense_group.id]  # Only this group
    )

    mock_expense_group_delete = mocker.patch.object(expense_group, 'delete')

    delete_expense_group_and_related_data(expense_group=expense_group, workspace_id=workspace_id)

    # Verify the error was deleted when mapping_error_expense_group_ids became empty (line 548)
    assert not Error.objects.filter(id=error_with_mapping.id).exists()

    mock_expense_group_delete.assert_called_once()


@pytest.mark.django_db()
def test_recreate_expense_groups_with_reimbursable_config(mocker, db):
    """
    Test recreate expense groups when reimbursable config exists
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    # Create personal expense
    personal_expense_data = data['expenses'][0].copy()
    personal_expense_data['org_id'] = workspace.fyle_org_id
    personal_expense_data['source_account_type'] = 'PERSONAL_CASH_ACCOUNT'

    expense_objects = Expense.create_expense_objects([personal_expense_data], workspace_id)
    expense_ids = [obj.id for obj in expense_objects]

    # Ensure reimbursable config exists (should not delete expenses)
    config = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    config.reimbursable_expenses_object = 'BILL'
    config.save()

    mock_delete_expenses = mocker.patch('apps.fyle.tasks.delete_expenses_in_db')

    recreate_expense_groups(workspace_id=workspace_id, expense_ids=expense_ids)

    # Should not call delete_expenses_in_db for reimbursable expenses
    mock_delete_expenses.assert_not_called()


@pytest.mark.django_db()
def test_recreate_expense_groups_with_ccc_config(mocker, db):
    """
    Test recreate expense groups when CCC config exists
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    # Create CCC expense
    ccc_expense_data = data['expenses'][0].copy()
    ccc_expense_data['org_id'] = workspace.fyle_org_id
    ccc_expense_data['source_account_type'] = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'

    expense_objects = Expense.create_expense_objects([ccc_expense_data], workspace_id)
    expense_ids = [obj.id for obj in expense_objects]

    # Ensure CCC config exists (should not delete expenses)
    config = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    config.corporate_credit_card_expenses_object = 'CREDIT_CARD_PURCHASE'
    config.save()

    mock_delete_expenses = mocker.patch('apps.fyle.tasks.delete_expenses_in_db')

    recreate_expense_groups(workspace_id=workspace_id, expense_ids=expense_ids)

    # Should not call delete_expenses_in_db for CCC expenses
    mock_delete_expenses.assert_not_called()


@pytest.mark.django_db()
def test_import_and_export_expenses_real_time_export_disabled(mocker, db):
    """
    Test import and export expenses with real-time export disabled to cover lines 354-355
    """
    from apps.workspaces.models import WorkspaceSchedule

    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    report_id = 'rp1s1L3QtMpF'

    # Create WorkspaceSchedule with real-time export disabled
    WorkspaceSchedule.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={'is_real_time_export_enabled': False}
    )

    # Create an expense group that will be found
    expense_data = data['expenses'][0].copy()
    expense_data['org_id'] = workspace.fyle_org_id
    expense_data['report_id'] = report_id
    expense_objects = Expense.create_expense_objects([expense_data], workspace_id)
    ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, workspace_id)

    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform_instance = mock_platform.return_value
    mock_platform_instance.expenses.get.return_value = [expense_data]

    mock_export = mocker.patch('apps.fyle.tasks.export_to_qbo')

    import_and_export_expenses(
        report_id=report_id,
        org_id=workspace.fyle_org_id,
        is_state_change_event=True,  # This triggers the real-time check
        report_state='APPROVED',
        imported_from=ExpenseImportSourceEnum.WEBHOOK
    )

    # Should not call export due to real-time export being disabled (line 355 return)
    mock_export.assert_not_called()

# Additional tests to improve coverage


@pytest.mark.django_db()
def test_create_expense_groups_configuration_update_import(mocker, db):
    """
    Test create_expense_groups with CONFIGURATION_UPDATE import to cover workspace save skip
    """
    workspace_id = 1

    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform_instance = mock_platform.return_value
    mock_platform_instance.expenses.get.return_value = []

    task_log = TaskLog.objects.create(workspace_id=workspace_id, type='FETCHING_EXPENSES', status='IN_PROGRESS')

    create_expense_groups(
        workspace_id,
        ['PERSONAL'],
        task_log,
        ExpenseImportSourceEnum.CONFIGURATION_UPDATE  # This should skip workspace.save()
    )

    assert task_log.status == 'COMPLETE'


@pytest.mark.django_db()
def test_sync_dimensions_categories_count_mismatch(mocker, db):
    """
    Test sync_dimensions when categories count doesn't match
    """
    workspace_id = 1

    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform_instance = mock_platform.return_value

    # Mock categories count to be different from expense attributes count
    mock_platform_instance.categories.get_count.return_value = 10
    mock_platform_instance.projects.get_count.return_value = 5

    # Mock the sync methods
    mock_platform_instance.categories.sync = mocker.MagicMock()
    mock_platform_instance.projects.sync = mocker.MagicMock()

    sync_dimensions(workspace_id, is_export=True)

    # Should call sync for both categories and projects due to count mismatch
    mock_platform_instance.categories.sync.assert_called_once()
    mock_platform_instance.projects.sync.assert_called_once()


@pytest.mark.django_db()
def test_sync_dimensions_no_export(mocker, db):
    """
    Test sync_dimensions when is_export=False
    """
    workspace_id = 1

    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform_instance = mock_platform.return_value

    sync_dimensions(workspace_id, is_export=False)

    # Should only call import_fyle_dimensions, not the count checks
    mock_platform_instance.import_fyle_dimensions.assert_called_once_with(is_export=False)
    mock_platform_instance.categories.get_count.assert_not_called()
    mock_platform_instance.projects.get_count.assert_not_called()


@pytest.mark.django_db()
def test_get_task_log_and_fund_source(mocker, db):
    """
    Test get_task_log_and_fund_source function
    """
    workspace_id = 1

    mock_get_fund_source = mocker.patch('apps.fyle.tasks.get_fund_source', return_value=['PERSONAL'])

    task_log, fund_source = get_task_log_and_fund_source(workspace_id)

    assert task_log.workspace_id == workspace_id
    assert task_log.type == 'FETCHING_EXPENSES'
    assert task_log.status == 'IN_PROGRESS'
    assert fund_source == ['PERSONAL']
    mock_get_fund_source.assert_called_once_with(workspace_id)


@pytest.mark.django_db()
def test_get_grouping_types_function(mocker, db):
    """
    Test get_grouping_types function
    """
    workspace_id = 1

    # Test with existing expense group settings
    result = get_grouping_types(workspace_id)

    # Should return grouping types based on expense group settings
    assert isinstance(result, dict)
    assert 'PERSONAL' in result
    assert 'CCC' in result

    # Test with no expense group settings
    ExpenseGroupSettings.objects.filter(workspace_id=workspace_id).delete()
    result = get_grouping_types(workspace_id)
    assert result == {}


@pytest.mark.django_db()
def test_import_and_export_expenses_state_change_simple(mocker, db):
    """
    Test import and export expenses with state change to cover line 339 - simplified version
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    report_id = 'rp1s1L3QtMpF'

    # Create a simple expense in the database first
    expense_data = data['expenses'][0].copy()
    expense_data['org_id'] = workspace.fyle_org_id
    expense_data['report_id'] = report_id

    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform_instance = mock_platform.return_value
    mock_platform_instance.expenses.get.return_value = [expense_data]

    # Mock filter_expenses_based_on_state to verify it's called (line 339)
    mock_filter_expenses = mocker.patch(
        'apps.fyle.tasks.filter_expenses_based_on_state',
        return_value=[expense_data]
    )

    import_and_export_expenses(
        report_id=report_id,
        org_id=workspace.fyle_org_id,
        is_state_change_event=True,  # This should trigger line 339
        imported_from=ExpenseImportSourceEnum.WEBHOOK
    )

    # Verify filter_expenses_based_on_state was called (line 339)
    mock_filter_expenses.assert_called_once()


@pytest.mark.django_db()
def test_recreate_expense_groups_delete_reimbursable_expenses(mocker, db):
    """
    Test recreate_expense_groups when reimbursable config is None - covers lines 574, 577-582
    """
    workspace_id = 1

    # Mock the initial expense filter to return actual expense objects
    mock_expense = mocker.MagicMock()
    mock_expense.fund_source = 'PERSONAL'
    mock_expense.id = 123

    mock_expense_filter = mocker.patch('apps.fyle.models.Expense.objects.filter')
    mock_expense_filter.return_value = [mock_expense]

    # Set reimbursable config to None to trigger deletion
    config = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    config.reimbursable_expenses_object = None
    config.save()

    mock_delete_expenses = mocker.patch('apps.fyle.tasks.delete_expenses_in_db')

    # Mock ExpenseGroup.create_expense_groups_by_report_id_fund_source to prevent further execution
    mock_create_groups = mocker.patch('apps.fyle.models.ExpenseGroup.create_expense_groups_by_report_id_fund_source')
    mock_create_groups.return_value = ([], [])

    recreate_expense_groups(workspace_id=workspace_id, expense_ids=[123])

    # Verify lines 574, 577-582: delete_expenses_in_db was called for reimbursable expenses
    mock_delete_expenses.assert_called_once_with(expense_ids=[123], workspace_id=workspace_id)


@pytest.mark.django_db()
def test_recreate_expense_groups_delete_ccc_expenses(mocker, db):
    """
    Test recreate_expense_groups when CCC config is None - covers lines 585-590
    """
    workspace_id = 1

    # Mock the initial expense filter to return actual expense objects
    mock_expense = mocker.MagicMock()
    mock_expense.fund_source = 'CCC'
    mock_expense.id = 456

    mock_expense_filter = mocker.patch('apps.fyle.models.Expense.objects.filter')
    mock_expense_filter.return_value = [mock_expense]

    # Set CCC config to None to trigger deletion
    config = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    config.corporate_credit_card_expenses_object = None
    config.save()

    mock_delete_expenses = mocker.patch('apps.fyle.tasks.delete_expenses_in_db')

    # Mock ExpenseGroup.create_expense_groups_by_report_id_fund_source to prevent further execution
    mock_create_groups = mocker.patch('apps.fyle.models.ExpenseGroup.create_expense_groups_by_report_id_fund_source')
    mock_create_groups.return_value = ([], [])

    recreate_expense_groups(workspace_id=workspace_id, expense_ids=[456])

    # Verify lines 585-590: delete_expenses_in_db was called for CCC expenses
    mock_delete_expenses.assert_called_once_with(expense_ids=[456], workspace_id=workspace_id)


@pytest.mark.django_db()
def test_recreate_expense_groups_with_filters(mocker, db):
    """
    Test recreate_expense_groups with expense filters - covers lines 593-598, 600-604
    """
    workspace_id = 1

    # Mock expense
    mock_expense = mocker.MagicMock()
    mock_expense.fund_source = 'PERSONAL'
    mock_expense.id = 789

    # Create a comprehensive mock queryset that supports chaining
    mock_expense_queryset = mocker.MagicMock()
    mock_expense_queryset.all.return_value = mock_expense_queryset
    mock_expense_queryset.values.return_value = mock_expense_queryset
    mock_expense_queryset.annotate.return_value = [{'fund_source': 'PERSONAL', 'total': 1, 'expense_ids': [789]}]
    mock_expense_filter = mocker.patch('apps.fyle.models.Expense.objects.filter')
    mock_expense_filter.return_value = mock_expense_queryset

    # Mock ExpenseFilter.objects.filter to return a filter
    mock_filter_queryset = mocker.patch('apps.fyle.models.ExpenseFilter.objects.filter')
    mock_filter_obj = mocker.MagicMock()
    mock_filter_obj.rank = 1
    mock_filter_queryset.return_value.order_by.return_value = [mock_filter_obj]

    mock_construct_filter = mocker.patch('apps.fyle.tasks.construct_expense_filter_query', return_value=Q())
    mock_skip_expenses = mocker.patch('apps.fyle.tasks.skip_expenses_and_post_accounting_export_summary')

    recreate_expense_groups(workspace_id=workspace_id, expense_ids=[789])

    # Verify lines 595-598: filter construction and skip_expenses was called
    mock_construct_filter.assert_called_once()
    mock_skip_expenses.assert_called()


@pytest.mark.django_db()
def test_recreate_expense_groups_with_skipped_expenses(mocker, db):
    """
    Test recreate_expense_groups when some expenses are skipped - covers lines 606, 610-615
    """

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
    workspace_id = 1

    # Mock expense
    mock_expense = mocker.MagicMock()
    mock_expense.fund_source = 'PERSONAL'
    mock_expense.id = 111

    mock_expense_filter = mocker.patch('apps.fyle.models.Expense.objects.filter')
    mock_expense_filter.return_value = [mock_expense]

    # Mock create_expense_groups to return skipped expense IDs
    skipped_ids = [999]
    mock_create_groups = mocker.patch(
        'apps.fyle.models.ExpenseGroup.create_expense_groups_by_report_id_fund_source',
        return_value=([], skipped_ids)
    )
    mock_skip_expenses = mocker.patch('apps.fyle.tasks.skip_expenses_and_post_accounting_export_summary')

    recreate_expense_groups(workspace_id=workspace_id, expense_ids=[111])

    # Verify lines 606, 610-615: expense group creation and skipped expense handling
    mock_create_groups.assert_called_once()
    mock_skip_expenses.assert_called()
    mock_logger.info.assert_any_call(
        "Some expenses were skipped during expense group re-creation: %s in workspace %s",
        skipped_ids, workspace_id
    )
    mock_logger.info.assert_any_call(
        "Successfully recreated expense groups for %s expenses in workspace %s",
        1, workspace_id
    )


@pytest.mark.django_db()
def test_recreate_expense_groups_simple_success_flow(mocker, db):
    """
    Test recreate_expense_groups simple success flow - covers lines 592, 606, 615
    """

    mock_create_groups = mocker.patch('apps.fyle.models.ExpenseGroup.create_expense_groups_by_report_id_fund_source', return_value=([], []))
    mock_logger = mocker.patch('apps.fyle.tasks.logger')
    workspace_id = 1

    # Mock expense
    mock_expense = mocker.MagicMock()
    mock_expense.fund_source = 'PERSONAL'
    mock_expense.id = 222

    mock_expense_filter = mocker.patch('apps.fyle.models.Expense.objects.filter')
    mock_expense_filter.return_value = [mock_expense]

    recreate_expense_groups(workspace_id=workspace_id, expense_ids=[222])

    # Verify lines 592, 606, 615: expense_objects assignment, group creation, success log
    mock_create_groups.assert_called_once()
    mock_logger.info.assert_any_call(
        "Successfully recreated expense groups for %s expenses in workspace %s",
        1, workspace_id
    )


@pytest.mark.django_db()
def test_import_and_export_expenses_real_time_export_enabled_simple(mocker, db):
    """
    Test import_and_export_expenses real-time export enabled - covers lines 349-358
    """

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    report_id = 'rp1s1L3QtMpF'

    # Mock expenses to return from platform
    expense_data = data['expenses'][0].copy()
    expense_data['org_id'] = workspace.fyle_org_id
    expense_data['report_id'] = report_id

    # Mock PlatformConnector
    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform_instance = mock_platform.return_value
    mock_platform_instance.expenses.get.return_value = [expense_data]

    # Mock expense group creation to return some expense group IDs
    mock_expense_groups = mocker.patch('apps.fyle.models.ExpenseGroup.objects.filter')
    mock_expense_groups.return_value.distinct.return_value.values.return_value = [{'id': 1}]

    # Mock WorkspaceSchedule to enable real-time export
    mock_workspace_schedule = mocker.patch('apps.workspaces.models.WorkspaceSchedule.objects.filter')
    mock_workspace_schedule.return_value.exists.return_value = True

    # Mock feature configuration to allow real-time export
    mock_feature_config = mocker.patch('apps.fyle.tasks.feature_configuration')
    mock_feature_config.feature.real_time_export_1hr_orgs = True

    mock_export = mocker.patch('apps.fyle.tasks.export_to_qbo')

    import_and_export_expenses(
        report_id=report_id,
        org_id=workspace.fyle_org_id,
        is_state_change_event=True,  # This triggers lines 349-358
        imported_from=ExpenseImportSourceEnum.WEBHOOK
    )

    # Verify lines 349-358: real-time export logic and export call
    mock_workspace_schedule.assert_called()
    mock_export.assert_called_once()
    mock_logger.info.assert_any_call(
        'Exporting expenses for workspace %s with expense group ids %s, triggered by %s',
        workspace.id, [1], ExpenseImportSourceEnum.WEBHOOK
    )


@pytest.mark.django_db()
def test_import_and_export_expenses_real_time_export_disabled_feature(mocker, db):
    """
    Test import_and_export_expenses when real-time export feature is disabled - covers lines 354-355
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    report_id = 'rp1s1L3QtMpF'

    # Mock expenses to return from platform
    expense_data = data['expenses'][0].copy()
    expense_data['org_id'] = workspace.fyle_org_id
    expense_data['report_id'] = report_id

    # Mock PlatformConnector
    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    mock_platform_instance = mock_platform.return_value
    mock_platform_instance.expenses.get.return_value = [expense_data]

    # Mock expense group creation to return some expense group IDs
    mock_expense_groups = mocker.patch('apps.fyle.models.ExpenseGroup.objects.filter')
    mock_expense_groups.return_value.distinct.return_value.values.return_value = [{'id': 1}]

    # Mock WorkspaceSchedule to enable real-time export
    mock_workspace_schedule = mocker.patch('apps.workspaces.models.WorkspaceSchedule.objects.filter')
    mock_workspace_schedule.return_value.exists.return_value = True

    # Mock feature configuration to DISABLE real-time export
    mock_feature_config = mocker.patch('apps.fyle.tasks.feature_configuration')
    mock_feature_config.feature.real_time_export_1hr_orgs = False

    mock_export = mocker.patch('apps.fyle.tasks.export_to_qbo')

    import_and_export_expenses(
        report_id=report_id,
        org_id=workspace.fyle_org_id,
        is_state_change_event=True,  # This triggers lines 349-355
        imported_from=ExpenseImportSourceEnum.WEBHOOK
    )

    # Verify lines 354-355: should return early, no export called
    mock_export.assert_not_called()


def test_import_and_export_expenses_exception_creates_task_log(mocker, db):
    """
    Test import_and_export_expenses exception when task_log is None - covers line 377
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    report_id = 'rp1s1L3QtMpF'

    # Mock to raise an exception early in the process
    mocker.patch('apps.fyle.helpers.get_fund_source', side_effect=Exception('Test exception'))

    mock_task_log_update_or_create = mocker.patch('apps.tasks.models.TaskLog.objects.update_or_create')
    mock_task_log_update_or_create.return_value = (TaskLog(workspace_id=workspace_id, type='FETCHING_EXPENSES', status='IN_PROGRESS'), True)

    mock_handle_exception = mocker.patch('apps.fyle.tasks.handle_import_exception')

    # Call without providing task_log (None by default)
    import_and_export_expenses(
        report_id=report_id,
        org_id=workspace.fyle_org_id,
        is_state_change_event=False,
        imported_from=ExpenseImportSourceEnum.DASHBOARD_SYNC
        # Note: not passing task_log, so it will be None
    )

    # Verify line 377: TaskLog.objects.update_or_create was called when task_log is None
    mock_task_log_update_or_create.assert_called_once_with(
        workspace_id=workspace.id,
        type='FETCHING_EXPENSES',
        defaults={'status': 'IN_PROGRESS'}
    )
    mock_handle_exception.assert_called_once()


def test_handle_fund_source_changes_with_actual_expense_groups_simple(mocker, db):
    """
    Test handle_fund_source_changes with actual expense groups - covers lines 454-477
    """

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
    workspace_id = 3
    changed_expense_ids = [123]

    # Create mock expense group
    mock_expense_group = mocker.MagicMock()
    mock_expense_group.id = 1
    mock_expense_group.expense_count = 1

    # Mock ExpenseGroup.objects.filter to return mock groups
    mock_expense_groups = mocker.patch('apps.fyle.models.ExpenseGroup.objects.filter')
    mock_queryset = mocker.MagicMock()
    mock_distinct_queryset = mocker.MagicMock()
    mock_distinct_queryset.__iter__ = lambda self: iter([mock_expense_group])
    mock_distinct_queryset.values_list.return_value = [123]
    mock_queryset.annotate.return_value.distinct.return_value = mock_distinct_queryset
    mock_expense_groups.return_value = mock_queryset

    # Mock construct_filter

    # Mock process_expense_group_for_fund_source_update to return True (processed)
    mock_process_group = mocker.patch(
        'apps.fyle.tasks.process_expense_group_for_fund_source_update',
        return_value=True
    )

    mock_recreate = mocker.patch('apps.fyle.tasks.recreate_expense_groups')
    mock_cleanup = mocker.patch('apps.fyle.tasks.cleanup_scheduled_task')

    handle_fund_source_changes_for_expense_ids(
        workspace_id=workspace_id,
        changed_expense_ids=changed_expense_ids,
        report_id='rp123',
        affected_fund_source_expense_ids={'PERSONAL': changed_expense_ids},
        task_name='test_task'
    )

    # Verify lines 454-477: affected_expense_ids populated, processing logic, recreation
    mock_process_group.assert_called_once()
    mock_logger.info.assert_any_call(
        "Processing fund source change for expense group %s with %s expenses in workspace %s",
        1, 1, workspace_id
    )
    mock_logger.info.assert_any_call(
        "All expense groups are exported or are not initiated, proceeding with recreation of expense groups for changed expense ids %s in workspace %s",
        changed_expense_ids, workspace_id
    )
    mock_recreate.assert_called_once_with(workspace_id=workspace_id, expense_ids=[123])
    mock_cleanup.assert_called_once_with(task_name='test_task', workspace_id=workspace_id)


@pytest.mark.django_db()
def test_handle_fund_source_changes_not_all_processed(mocker, db):
    """
    Test handle_fund_source_changes when not all groups are processed - covers lines 468-469, 476-477
    """

    mock_logger = mocker.patch('apps.fyle.tasks.logger')
    workspace_id = 3
    changed_expense_ids = [456]

    # Create mock expense group
    mock_expense_group = mocker.MagicMock()
    mock_expense_group.id = 2
    mock_expense_group.expense_count = 1

    # Mock ExpenseGroup.objects.filter to return mock groups
    mock_expense_groups = mocker.patch('apps.fyle.models.ExpenseGroup.objects.filter')
    mock_queryset = mocker.MagicMock()
    mock_distinct_queryset = mocker.MagicMock()
    mock_distinct_queryset.__iter__ = lambda self: iter([mock_expense_group])
    mock_distinct_queryset.values_list.return_value = [456]
    mock_queryset.annotate.return_value.distinct.return_value = mock_distinct_queryset
    mock_expense_groups.return_value = mock_queryset

    # Mock construct_filter

    # Mock process_expense_group_for_fund_source_update to return False (not processed)
    mock_process_group = mocker.patch(
        'apps.fyle.tasks.process_expense_group_for_fund_source_update',
        return_value=False
    )

    mock_recreate = mocker.patch('apps.fyle.tasks.recreate_expense_groups')
    mock_cleanup = mocker.patch('apps.fyle.tasks.cleanup_scheduled_task')

    handle_fund_source_changes_for_expense_ids(
        workspace_id=workspace_id,
        changed_expense_ids=changed_expense_ids,
        report_id='rp456',
        affected_fund_source_expense_ids={'PERSONAL': changed_expense_ids}
    )

    # Verify lines 468-469, 476-477: not all processed, skip recreation
    mock_process_group.assert_called_once()
    mock_logger.info.assert_any_call(
        "Not all expense groups are exported, skipping recreation of expense groups for changed expense ids %s in workspace %s",
        changed_expense_ids, workspace_id
    )
    mock_recreate.assert_not_called()
    mock_cleanup.assert_not_called()


def test_handle_expense_report_change_added_to_report(db, mocker):
    """
    Test handle_expense_report_change with ADDED_TO_REPORT action
    """
    workspace = Workspace.objects.get(id=3)

    expense_data = {
        'id': 'tx1234567890',
        'org_id': workspace.fyle_org_id,
        'report_id': 'rp1234567890'
    }

    mock_delete = mocker.patch('apps.fyle.tasks._delete_expense_groups_for_report')

    handle_expense_report_change(expense_data, 'ADDED_TO_REPORT')

    mock_delete.assert_called_once()
    args = mock_delete.call_args[0]
    assert args[0] == 'rp1234567890'
    assert args[1].id == workspace.id


def test_handle_expense_report_change_ejected_from_report(db, mocker, add_expense_report_data):
    """
    Test handle_expense_report_change with EJECTED_FROM_REPORT action
    """
    workspace = Workspace.objects.get(id=3)
    expense = add_expense_report_data['expenses'][0]

    expense_data = {
        'id': expense.expense_id,
        'org_id': workspace.fyle_org_id,
        'report_id': expense.report_id
    }

    mock_handle = mocker.patch('apps.fyle.tasks._handle_expense_ejected_from_report')

    handle_expense_report_change(expense_data, 'EJECTED_FROM_REPORT')

    mock_handle.assert_called_once()


def test_delete_expense_groups_for_report_basic(db, mocker, add_expense_report_data):
    """
    Test _delete_expense_groups_for_report deletes non-exported expense groups
    """
    workspace = Workspace.objects.get(id=3)

    expense = add_expense_report_data['expenses'][0]
    report_id = expense.report_id

    mock_delete = mocker.patch('apps.fyle.tasks.delete_expense_group_and_related_data')

    _delete_expense_groups_for_report(report_id, workspace)

    assert mock_delete.called


def test_delete_expense_groups_for_report_no_expenses(db, mocker):
    """
    Test _delete_expense_groups_for_report with no expenses in database
    Case: Non-existent report_id
    """
    workspace = Workspace.objects.get(id=3)
    report_id = 'rpNonExistent123'

    _delete_expense_groups_for_report(report_id, workspace)


def test_delete_expense_groups_for_report_with_active_task_logs(db, mocker, add_expense_report_data):
    """
    Test _delete_expense_groups_for_report skips groups with active task logs
    """
    workspace = Workspace.objects.get(id=3)
    expense_group = add_expense_report_data['expense_group']

    TaskLog.objects.create(
        workspace_id=workspace.id,
        expense_group_id=expense_group.id,
        type='CREATING_BILL',
        status='IN_PROGRESS'
    )

    report_id = expense_group.expenses.first().report_id

    mock_delete = mocker.patch('apps.fyle.tasks.delete_expense_group_and_related_data')

    _delete_expense_groups_for_report(report_id, workspace)

    assert not mock_delete.called


def test_delete_expense_groups_for_report_preserves_exported(db, mocker, add_expense_report_data):
    """
    Test _delete_expense_groups_for_report preserves exported expense groups
    """
    workspace = Workspace.objects.get(id=3)

    expense_group = add_expense_report_data['expense_group']

    expense_group.exported_at = datetime.now(tz=timezone.utc)
    expense_group.save()

    report_id = expense_group.expenses.first().report_id

    mock_delete = mocker.patch('apps.fyle.tasks.delete_expense_group_and_related_data')

    _delete_expense_groups_for_report(report_id, workspace)

    assert not mock_delete.called


def test_handle_expense_ejected_from_report_removes_from_group(db, add_expense_report_data):
    """
    Test _handle_expense_ejected_from_report removes expense from group
    """
    workspace = Workspace.objects.get(id=3)

    expense_group = add_expense_report_data['expense_group']
    expenses = add_expense_report_data['expenses']

    expense_to_remove = expenses[0]

    expense_data = {
        'id': expense_to_remove.expense_id,
        'report_id': None
    }

    initial_expense_count = expense_group.expenses.count()

    _handle_expense_ejected_from_report(expense_to_remove, expense_data, workspace)

    expense_group.refresh_from_db()

    assert expense_group.expenses.count() == initial_expense_count - 1
    assert expense_to_remove not in expense_group.expenses.all()
    assert ExpenseGroup.objects.filter(id=expense_group.id).exists()


def test_handle_expense_ejected_from_report_deletes_empty_group(db, add_expense_report_data):
    """
    Test _handle_expense_ejected_from_report deletes group when last expense is removed
    """
    workspace = Workspace.objects.get(id=3)

    expense_group = add_expense_report_data['expense_group']
    expense = add_expense_report_data['expenses'][0]
    expense_group.expenses.set([expense])

    expense_data = {
        'id': expense.expense_id,
        'report_id': None
    }

    group_id = expense_group.id

    _handle_expense_ejected_from_report(expense, expense_data, workspace)

    assert not ExpenseGroup.objects.filter(id=group_id).exists()


def test_handle_expense_ejected_from_report_no_group_found(db):
    """
    Test _handle_expense_ejected_from_report when expense has no group
    """
    workspace = Workspace.objects.get(id=3)

    expense = Expense.objects.create(
        workspace_id=workspace.id,
        expense_id='txOrphanExpense123',
        employee_email='test@example.com',
        category='Test',
        amount=100,
        currency='USD',
        org_id=workspace.fyle_org_id,
        settlement_id='setl123',
        report_id='rp123',
        spent_at='2024-01-01T00:00:00Z',
        expense_created_at='2024-01-01T00:00:00Z',
        expense_updated_at='2024-01-01T00:00:00Z',
        fund_source='PERSONAL'
    )

    expense_data = {
        'id': expense.expense_id,
        'report_id': None
    }

    _handle_expense_ejected_from_report(expense, expense_data, workspace)


def test_handle_expense_ejected_from_report_with_active_task_log(db, add_expense_report_data):
    """
    Test _handle_expense_ejected_from_report skips removal when task log is active
    """
    workspace = Workspace.objects.get(id=3)

    expense_group = add_expense_report_data['expense_group']
    expense = add_expense_report_data['expenses'][0]
    initial_count = expense_group.expenses.count()

    TaskLog.objects.create(
        workspace_id=workspace.id,
        expense_group_id=expense_group.id,
        type='CREATING_BILL',
        status='ENQUEUED'
    )

    expense_data = {
        'id': expense.expense_id,
        'report_id': None
    }

    _handle_expense_ejected_from_report(expense, expense_data, workspace)

    expense_group.refresh_from_db()

    assert expense_group.expenses.count() == initial_count
    assert expense in expense_group.expenses.all()


def test_handle_expense_report_change_ejected_expense_not_found(db, mocker):
    """
    Test handle_expense_report_change when expense doesn't exist in workspace (EJECTED_FROM_REPORT)
    """
    workspace = Workspace.objects.get(id=3)

    expense_data = {
        'id': 'txNonExistent999',
        'org_id': workspace.fyle_org_id,
        'report_id': None
    }

    handle_expense_report_change(expense_data, 'EJECTED_FROM_REPORT')


def test_handle_expense_report_change_ejected_from_exported_group(db, add_expense_report_data):
    """
    Test handle_expense_report_change skips when expense is part of exported group (EJECTED_FROM_REPORT)
    """
    workspace = Workspace.objects.get(id=3)
    expense_group = add_expense_report_data['expense_group']
    expense = add_expense_report_data['expenses'][0]

    expense_group.exported_at = datetime.now(tz=timezone.utc)
    expense_group.save()

    expense_data = {
        'id': expense.expense_id,
        'org_id': workspace.fyle_org_id,
        'report_id': None
    }

    handle_expense_report_change(expense_data, 'EJECTED_FROM_REPORT')

    expense_group.refresh_from_db()
    assert expense in expense_group.expenses.all()


def test_handle_category_changes_for_expense(db, add_category_test_expense, add_category_test_expense_group, add_category_mapping_error, add_category_expense_attribute):
    workspace = Workspace.objects.get(id=3)
    expense = add_category_test_expense
    expense_group = add_category_test_expense_group
    error = add_category_mapping_error

    error.mapping_error_expense_group_ids = [expense_group.id, 999]
    error.save()

    handle_category_changes_for_expense(expense=expense, new_category='New Category')

    error.refresh_from_db()
    assert expense_group.id not in error.mapping_error_expense_group_ids
    assert 999 in error.mapping_error_expense_group_ids

    error.mapping_error_expense_group_ids = [expense_group.id]
    error.save()

    handle_category_changes_for_expense(expense=expense, new_category='Another Category')

    assert not Error.objects.filter(id=error.id, workspace_id=workspace.id, type='CATEGORY_MAPPING').exists()

    expense_group.delete()

    expense_group_2 = ExpenseGroup.objects.create(
        workspace_id=workspace.id,
        fund_source='PERSONAL',
        description={'employee_email': expense.employee_email},
        employee_name=expense.employee_name
    )
    expense_group_2.expenses.add(expense)

    category_attribute = add_category_expense_attribute
    category_attribute.pk = None
    category_attribute.id = None
    category_attribute.value = 'Test Category With Error'
    category_attribute.source_id = 'catErr123'
    category_attribute.save()

    existing_error = Error.objects.create(
        workspace_id=workspace.id,
        type='CATEGORY_MAPPING',
        is_resolved=False,
        expense_attribute=category_attribute,
        mapping_error_expense_group_ids=[888]
    )

    handle_category_changes_for_expense(expense=expense, new_category='Test Category With Error')

    existing_error.refresh_from_db()
    assert expense_group_2.id in existing_error.mapping_error_expense_group_ids
    assert 888 in existing_error.mapping_error_expense_group_ids

    expense_group_2.delete()

    expense_group_3 = ExpenseGroup.objects.create(
        workspace_id=workspace.id,
        fund_source='PERSONAL',
        description={'employee_email': expense.employee_email},
        employee_name=expense.employee_name
    )
    expense_group_3.expenses.add(expense)

    category_attribute_2 = add_category_expense_attribute
    category_attribute_2.pk = None
    category_attribute_2.id = None
    category_attribute_2.value = 'Unmapped Category'
    category_attribute_2.source_id = 'catUnmapped456'
    category_attribute_2.save()

    handle_category_changes_for_expense(expense=expense, new_category='Unmapped Category')

    new_error = Error.objects.filter(
        workspace_id=workspace.id,
        type='CATEGORY_MAPPING',
        expense_attribute=category_attribute_2
    ).first()

    assert new_error is not None
    assert expense_group_3.id in new_error.mapping_error_expense_group_ids
    assert new_error.error_title == 'Unmapped Category'
    assert new_error.error_detail == 'Category mapping is missing'


def test_update_non_exported_expenses_category_change(mocker, db):
    expense_data = data['raw_expense'].copy()
    expense_data['category']['name'] = 'New Category'
    expense_data['category']['sub_category'] = 'New Sub Category'
    org_id = expense_data['org_id']

    default_raw_expense = data['default_raw_expense'].copy()
    default_raw_expense['category'] = 'Old Category'
    default_raw_expense['sub_category'] = 'Old Sub Category'

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

    # Mock FyleCredential
    mocker.patch('apps.fyle.tasks.FyleCredential.objects.get')

    mock_platform = mocker.patch('apps.fyle.tasks.PlatformConnector')
    constructed_expense = expense_data.copy()
    constructed_expense['category'] = expense_data['category']['name']
    constructed_expense['sub_category'] = expense_data['category']['sub_category']
    constructed_expense['source_account_type'] = 'PERSONAL_CASH_ACCOUNT'
    mock_platform.return_value.expenses.construct_expense_object.return_value = [constructed_expense]

    mocker.patch('apps.fyle.tasks.Expense.create_expense_objects', return_value=None)

    mock_handle_category_changes = mocker.patch(
        'apps.fyle.tasks.handle_category_changes_for_expense',
        return_value=None
    )

    update_non_exported_expenses(expense_data)

    assert mock_handle_category_changes.call_count == 1
    _, kwargs = mock_handle_category_changes.call_args
    assert kwargs['expense'] == expense_created
    assert kwargs['new_category'] == 'New Category / New Sub Category'

    expense_created.category = 'Same Category'
    expense_created.sub_category = 'Same Category'
    expense_created.save()

    expense_data_2 = data['raw_expense'].copy()
    expense_data_2['category']['name'] = 'Changed'
    expense_data_2['category']['sub_category'] = 'Changed'

    constructed_expense_2 = expense_data_2.copy()
    constructed_expense_2['category'] = 'Changed'
    constructed_expense_2['sub_category'] = 'Changed'
    constructed_expense_2['source_account_type'] = 'PERSONAL_CASH_ACCOUNT'
    mock_platform.return_value.expenses.construct_expense_object.return_value = [constructed_expense_2]

    update_non_exported_expenses(expense_data_2)

    assert mock_handle_category_changes.call_count == 2
    _, kwargs = mock_handle_category_changes.call_args
    assert kwargs['new_category'] == 'Changed'

    expense_created.category = 'Old Cat'
    expense_created.sub_category = None
    expense_created.save()

    expense_data_3 = data['raw_expense'].copy()
    expense_data_3['category']['name'] = 'New Cat'
    expense_data_3['category']['sub_category'] = None

    constructed_expense_3 = expense_data_3.copy()
    constructed_expense_3['category'] = 'New Cat'
    constructed_expense_3['sub_category'] = None
    constructed_expense_3['source_account_type'] = 'PERSONAL_CASH_ACCOUNT'
    mock_platform.return_value.expenses.construct_expense_object.return_value = [constructed_expense_3]

    update_non_exported_expenses(expense_data_3)

    assert mock_handle_category_changes.call_count == 3
    _, kwargs = mock_handle_category_changes.call_args
    assert kwargs['new_category'] == 'New Cat'


def test_handle_org_setting_updated(db):
    """
    Test handle_org_setting_updated stores regional_settings in org_settings field
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    workspace.org_settings = {}
    workspace.save()

    handle_org_setting_updated(
        workspace_id=workspace_id,
        org_settings=data['org_settings']['org_settings_payload']
    )

    workspace.refresh_from_db()

    assert workspace.org_settings == data['org_settings']['expected_org_settings']
    assert 'other_setting' not in workspace.org_settings


def test_handle_org_setting_updated_empty_regional_settings(db):
    """
    Test handle_org_setting_updated when regional_settings is empty or missing
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    handle_org_setting_updated(
        workspace_id=workspace_id,
        org_settings=data['org_settings']['org_settings_payload_without_regional']
    )

    workspace.refresh_from_db()
    assert workspace.org_settings == data['org_settings']['expected_org_settings_empty']


def test_handle_org_setting_updated_overwrites_existing(db):
    """
    Test handle_org_setting_updated overwrites existing org_settings
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    workspace.org_settings = data['org_settings']['expected_org_settings']
    workspace.save()

    handle_org_setting_updated(
        workspace_id=workspace_id,
        org_settings=data['org_settings']['org_settings_payload_updated']
    )

    workspace.refresh_from_db()
    assert workspace.org_settings == data['org_settings']['expected_org_settings_updated']
