from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.exceptions import handle_qbo_exceptions
from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential


def test_handle_qbo_exceptions(mocker, db):
    """
    Test handle_qbo_exceptions decorator
    """
    @handle_qbo_exceptions(bill_payment=True)
    def test_func(bill_obj, workspace_id, task_log):
        raise FyleCredential.DoesNotExist

    # Create mock expense objects
    mock_expense1 = mocker.MagicMock()
    mock_expense1.id = 1
    mock_expense2 = mocker.MagicMock()
    mock_expense2.id = 2

    # Create a mock expense queryset
    mock_expenses_queryset = mocker.MagicMock()
    mock_expenses_queryset.all.return_value = [mock_expense1, mock_expense2]

    # Create a mock expense group
    mock_expense_group = mocker.MagicMock(spec=ExpenseGroup)
    mock_expense_group.workspace_id = 1
    mock_expense_group.fund_source = 'PERSONAL'
    mock_expense_group.expenses = mock_expenses_queryset

    # Create a mock bill object that has an expense_group attribute
    mock_bill = mocker.MagicMock()
    mock_bill.expense_group = mock_expense_group

    mock_task_log = mocker.MagicMock(spec=TaskLog)
    mock_workspace_id = 1

    # Mock the post_accounting_export_summary function to avoid database calls
    mocker.patch('apps.quickbooks_online.exceptions.post_accounting_export_summary')

    test_func(mock_bill, mock_workspace_id, mock_task_log)

    # Verify that task_log was updated correctly
    assert mock_task_log.detail == {'message': 'Fyle credentials do not exist in workspace'}
    assert mock_task_log.status == 'FAILED'
    mock_task_log.save.assert_called_once()
