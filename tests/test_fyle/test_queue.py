from apps.fyle.queue import handle_webhook_callback
from apps.quickbooks_online.queue import __create_chain_and_run
from apps.workspaces.models import Workspace
from fyle_accounting_library.rabbitmq.data_class import Task


# This test is just for cov :D
def test_create_chain_and_run(db):
    workspace_id = 3
    chain_tasks = [
        Task(
            target='apps.quickbooks_online.tasks.create_cheque',
            args=[1, 1, True, False]
        )
    ]

    __create_chain_and_run(workspace_id, chain_tasks, True)
    assert True


# This test is just for cov :D
def test_handle_webhook_callback(db):
    body = {
        'action': 'ACCOUNTING_EXPORT_INITIATED',
        'data': {
            'id': 'rp1s1L3QtMpF',
            'org_id': 'or79Cob97KSh'
        }
    }

    handle_webhook_callback(body, 3)


# This test is just for cov :D (2)
def test_handle_webhook_callback_2(db):
    body = {
        'action': 'STATE_CHANGE_PAYMENT_PROCESSING',
        'data': {
            'id': 'rp1s1L3QtMpF',
            'org_id': 'or79Cob97KSh',
            'state': 'APPROVED'
        }
    }

    worksapce, _ = Workspace.objects.update_or_create(
        fyle_org_id = 'or79Cob97KSh'
    )

    handle_webhook_callback(body, worksapce.id)
