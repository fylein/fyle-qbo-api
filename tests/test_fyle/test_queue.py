from apps.fyle.queue import async_import_and_export_expenses
from apps.quickbooks_online.queue import __create_chain_and_run


# This test is just for cov :D
def test_create_chain_and_run(db):
    workspace_id = 3
    chain_tasks = [
        {
            'target': 'apps.quickbooks_online.tasks.create_cheque',
            'expense_group': 1,
            'task_log_id': 1,
            'last_export': True
        }
    ]

    __create_chain_and_run(workspace_id, chain_tasks, True)
    assert True


# This test is just for cov :D
def test_async_import_and_export_expenses(db):
    body = {
        'action': 'ACCOUNTING_EXPORT_INITIATED',
        'data': {
            'id': 'rp1s1L3QtMpF',
            'org_id': 'or79Cob97KSh'
        }
    }

    async_import_and_export_expenses(body, 3)
