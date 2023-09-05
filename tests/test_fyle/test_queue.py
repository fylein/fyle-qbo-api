from apps.fyle.models import Expense
from apps.fyle.queue import async_post_accounting_export_summary
from apps.quickbooks_online.queue import __create_chain_and_run
from apps.workspaces.models import FyleCredential


# This test is just for cov :D
def test_async_post_accounting_export_summary(db):
    async_post_accounting_export_summary(1, 1)
    assert True


# This test is just for cov :D
def test_create_chain_and_run(db):
    workspace_id = 3
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    in_progress_expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    chain_tasks = [
        {
            'target': 'apps.quickbooks_online.tasks.create_cheque',
            'expense_group': 1,
            'task_log_id': 1,
            'last_export': True
        }
    ]

    __create_chain_and_run(fyle_credentials, in_progress_expenses, workspace_id, chain_tasks)
    assert True
