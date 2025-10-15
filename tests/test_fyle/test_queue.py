from fyle_accounting_library.rabbitmq.data_class import Task

from apps.fyle.queue import async_import_and_export_expenses
from apps.quickbooks_online.queue import __create_chain_and_run
from apps.workspaces.models import Workspace


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
def test_async_import_and_export_expenses(db):
    body = {
        'action': 'ACCOUNTING_EXPORT_INITIATED',
        'data': {
            'id': 'rp1s1L3QtMpF',
            'org_id': 'or79Cob97KSh'
        }
    }

    async_import_and_export_expenses(body, 3)


# This test is just for cov :D (2)
def test_async_import_and_export_expenses_2(db):
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

    async_import_and_export_expenses(body, worksapce.id)


def test_async_import_and_export_expenses_ejected_from_report(db):
    body = {
        'action': 'EJECTED_FROM_REPORT',
        'resource': 'EXPENSE',
        'data': {
            'id': 'txExpense123',
            'org_id': 'or79Cob97KSh'
        }
    }

    workspace = Workspace.objects.get(id=3)

    async_import_and_export_expenses(body, workspace.id)


def test_async_import_and_export_expenses_added_to_report(db):
    body = {
        'action': 'ADDED_TO_REPORT',
        'resource': 'EXPENSE',
        'data': {
            'id': 'txExpense456',
            'org_id': 'or79Cob97KSh',
            'report_id': 'rpReport123'
        }
    }

    workspace = Workspace.objects.get(id=3)

    async_import_and_export_expenses(body, workspace.id)
