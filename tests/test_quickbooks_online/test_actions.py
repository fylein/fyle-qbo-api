from unittest import mock
from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.actions import generate_export_url_and_update_expense, refresh_quickbooks_dimensions, sync_quickbooks_dimensions
from apps.workspaces.models import Workspace


def test_generate_export_url_and_update_expense(db):
    expense_group = ExpenseGroup.objects.filter(id=15).first()
    generate_export_url_and_update_expense(expense_group)

    expense_group = ExpenseGroup.objects.filter(id=15).first()

    for expense in expense_group.expenses.all():
        assert expense.accounting_export_summary['url'] == 'https://lolo.qbo.com/app/expense?txnId=370'
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['error_type'] == None
        assert expense.accounting_export_summary['id'] == expense.expense_id
        assert expense.accounting_export_summary['state'] == 'COMPLETE'


def test_refresh_quickbooks_dimensions(db):
    workspace_id = 1
    workspace = Workspace.objects.get(id=3)

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.sync_dimensions') as mock_call:
        mock_call.return_value = None

        refresh_quickbooks_dimensions(workspace_id)
        assert workspace.destination_synced_at is not None


def test_sync_quickbooks_dimensions(db):
    workspace = Workspace.objects.get(id=3)

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.sync_dimensions') as mock_call:
        mock_call.return_value = None

        sync_quickbooks_dimensions(3)
        assert workspace.destination_synced_at is not None

        # If dimensions were synced ≤ 1 day ago, they shouldn't be synced again
        old_destination_synced_at = workspace.destination_synced_at
        sync_quickbooks_dimensions(3)
        assert workspace.destination_synced_at == old_destination_synced_at
