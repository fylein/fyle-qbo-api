import json
from unittest import mock

from django.db import Error
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
    skip_expenses_pre_export,
)
from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential, LastExportDetail, Workspace, WorkspaceGeneralSettings
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

    assert expense_created.category == 'Old Category'

    update_non_exported_expenses(payload['data'])

    expense = Expense.objects.get(expense_id='txhJLOSKs1iN', org_id=org_id)
    assert expense.category == 'ABN Withholding'

    expense.accounting_export_summary = {"synced": True, "state": "COMPLETE"}
    expense.category = 'Old Category'
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


@pytest.mark.django_db()
def test_skip_expenses_pre_export(db):
    """
    Test skip_expenses_pre_export functionality
    """
    # Create expense filters
    ExpenseFilter.objects.create(
        workspace_id=1,
        condition='employee_email',
        operator='in',
        values=['jhonsnow@fyle.in'],
        rank=1
    )

    # First create some expenses and expense groups
    expenses = list(data["expenses_spent_at"])
    for expense in expenses:
        expense['org_id'] = 'orHVw3ikkCxJ'
        expense['employee_email'] = 'regular.user@fyle.in'  # Set a non-matching email

    expense_objects = Expense.create_expense_objects(expenses, 1)
    expense_groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, 1)

    # Create task log and error for one expense group
    expense_group = expense_groups[0]
    task_log = TaskLog.objects.create(
        workspace_id=1,
        expense_group=expense_group,
        type='CREATING_BILL',
        status='IN_PROGRESS'
    )

    error = Error.objects.create(
        workspace_id=1,
        expense_group=expense_group,
        type='MAPPING',
        error_title='Test error'
    )

    # Create LastExportDetail with failed count
    LastExportDetail.objects.create(
        workspace_id=1,
        failed_count=1
    )

    # Verify initial state
    assert Expense.objects.filter(org_id='orHVw3ikkCxJ', is_skipped=True).count() == 0
    assert Expense.objects.filter(org_id='orHVw3ikkCxJ', is_skipped=False).count() == 3
    assert TaskLog.objects.filter(workspace_id=1).count() == 1
    assert Error.objects.filter(workspace_id=1).count() == 1

    # Now update some expenses to match filter criteria
    expenses_to_update = Expense.objects.filter(org_id='orHVw3ikkCxJ')[:2]
    for expense in expenses_to_update:
        expense.employee_email = 'jhonsnow@fyle.in'
        expense.save()

    # Run skip_expenses_pre_export
    skip_expenses_pre_export(1, None)

    # Verify that matching expenses are skipped
    assert Expense.objects.filter(org_id='orHVw3ikkCxJ', is_skipped=True).count() == 2
    assert Expense.objects.filter(org_id='orHVw3ikkCxJ', is_skipped=False).count() == 1

    # Verify cleanup of related objects
    assert TaskLog.objects.filter(workspace_id=1).count() == 0
    assert Error.objects.filter(workspace_id=1).count() == 0

    # Verify LastExportDetail failed count is reset
    last_export_detail = LastExportDetail.objects.get(workspace_id=1)
    assert last_export_detail.failed_count == 0

    # Verify expense groups are properly updated/deleted
    for expense in expenses_to_update:
        assert not ExpenseGroup.objects.filter(expenses__id=expense.id).exists()
