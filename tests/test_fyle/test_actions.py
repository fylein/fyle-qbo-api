from unittest import mock

from django.conf import settings
from django.db.models import Q
from fyle.platform.exceptions import InternalServerError, RetryException, WrongParamsError
from fyle_integrations_platform_connector import PlatformConnector

from apps.fyle.actions import (
    bulk_post_accounting_export_summary,
    create_generator_and_post_in_batches,
    mark_accounting_export_summary_as_synced,
    mark_expenses_as_skipped,
    refresh_fyle_dimension,
    sync_fyle_dimensions,
    update_complete_expenses,
    update_expenses_in_progress,
    update_failed_expenses,
)
from apps.fyle.helpers import get_updated_accounting_export_summary
from apps.fyle.models import Expense, ExpenseGroup
from apps.workspaces.models import FyleCredential, Workspace


def test_update_expenses_in_progress(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    update_expenses_in_progress(expenses)

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['state'] == 'IN_PROGRESS'
        assert expense.accounting_export_summary['url'] == '{}/main/dashboard'.format(
            settings.QBO_INTEGRATION_APP_URL
        )
        assert expense.accounting_export_summary['error_type'] == None
        assert expense.accounting_export_summary['id'] == expense.expense_id


def test_mark_expenses_as_skipped(db):
    expense_group = ExpenseGroup.objects.filter(workspace_id=3).first()
    expense_id = expense_group.expenses.first().id
    expense_group.expenses.remove(expense_id)

    workspace = Workspace.objects.get(id=3)
    mark_expenses_as_skipped(Q(), [expense_id], workspace)

    expense = Expense.objects.filter(id=expense_id).first()

    assert expense.is_skipped == True
    assert expense.accounting_export_summary['synced'] == False


def test_mark_accounting_export_summary_as_synced(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    for expense in expenses:
        expense.accounting_export_summary = get_updated_accounting_export_summary(
            'tx_123',
            'SKIPPED',
            None,
            '{}/main/export_log'.format(settings.QBO_INTEGRATION_APP_URL),
            True
        )
        expense.save()

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    mark_accounting_export_summary_as_synced(expenses)

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == True


def test_update_failed_expenses(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    update_failed_expenses(expenses, True)

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['state'] == 'ERROR'
        assert expense.accounting_export_summary['error_type'] == 'MAPPING'
        assert expense.accounting_export_summary['url'] == '{}/main/dashboard'.format(
            settings.QBO_INTEGRATION_APP_URL
        )
        assert expense.accounting_export_summary['id'] == expense.expense_id


def test_update_complete_expenses(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    update_complete_expenses(expenses, 'https://qbo.google.com')

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['state'] == 'COMPLETE'
        assert expense.accounting_export_summary['error_type'] == None
        assert expense.accounting_export_summary['url'] == 'https://qbo.google.com'
        assert expense.accounting_export_summary['id'] == expense.expense_id


def test_bulk_post_accounting_export_summary(db):
    fyle_credentails = FyleCredential.objects.get(workspace_id=3)
    platform = PlatformConnector(fyle_credentails)

    with mock.patch('fyle.platform.apis.v1.admin.Expenses.post_bulk_accounting_export_summary') as mock_call:
        mock_call.side_effect = InternalServerError('Timeout')
        try:
            bulk_post_accounting_export_summary(platform, {})
        except RetryException:
            assert mock_call.call_count == 3


def test_create_generator_and_post_in_batches(db):
    fyle_credentails = FyleCredential.objects.get(workspace_id=3)
    platform = PlatformConnector(fyle_credentails)

    with mock.patch('fyle.platform.apis.v1.admin.Expenses.post_bulk_accounting_export_summary') as mock_call:
        mock_call.side_effect = RetryException('Timeout')
        try:
            create_generator_and_post_in_batches([{
                'id': 'txxTi9ZfdepC'
            }], platform, 3)

            # Exception should be handled
            assert True
        except RetryException:
            # This should not be reached
            assert False


def test_handle_post_accounting_export_summary_exception(db):
    fyle_credentails = FyleCredential.objects.get(workspace_id=3)
    platform = PlatformConnector(fyle_credentails)
    expense = Expense.objects.filter(org_id='or79Cob97KSh').first()
    expense.workspace_id = 3
    expense.save()

    expense_id = expense.expense_id

    with mock.patch('fyle.platform.apis.v1.admin.Expenses.post_bulk_accounting_export_summary') as mock_call:
        mock_call.side_effect = WrongParamsError('Some of the parameters are wrong', {
            'data': [
                {
                    'message': 'Permission denied to perform this action.',
                    'key': expense_id
                }
            ]
        })
        create_generator_and_post_in_batches([{
            'id': expense_id
        }], platform, 3)

    expense = Expense.objects.get(expense_id=expense_id)

    assert expense.accounting_export_summary['synced'] == True
    assert expense.accounting_export_summary['state'] == 'DELETED'
    assert expense.accounting_export_summary['error_type'] == None
    assert expense.accounting_export_summary['url'] == '{}/main/dashboard'.format(
        settings.QBO_INTEGRATION_APP_URL
    )
    assert expense.accounting_export_summary['id'] == expense_id


def test_sync_fyle_dimensions(db):
    workspace = Workspace.objects.get(id=3)

    with mock.patch('fyle_integrations_platform_connector.fyle_integrations_platform_connector.PlatformConnector.import_fyle_dimensions') as mock_call:
        mock_call.return_value = None

        sync_fyle_dimensions(3)
        assert workspace.source_synced_at is not None

        # If dimensions were synced ≤ 1 day ago, they shouldn't be synced again
        old_source_synced_at = workspace.source_synced_at
        sync_fyle_dimensions(3)
        assert workspace.source_synced_at == old_source_synced_at


def test_refresh_fyle_dimension(db):
    workspace = Workspace.objects.get(id=3)

    with mock.patch('fyle_integrations_platform_connector.fyle_integrations_platform_connector.PlatformConnector.import_fyle_dimensions') as mock_call:
        mock_call.return_value = None

        refresh_fyle_dimension(3)
        assert workspace.source_synced_at is not None
