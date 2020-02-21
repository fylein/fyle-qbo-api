from apps.fyle.tasks import create_expense_groups
from apps.quickbooks_online.tasks import create_bills
from apps.tasks.models import TaskLog


def run_sync_schedule(workspace_id):
    """
    Run schedule
    :param workspace_id: 
    :return: 
    """
    task_log: TaskLog = create_expense_groups(
        workspace_id=workspace_id, state=['PAYMENT_PROCESSING'],
        export_non_reimbursable=False
    )
    while task_log.status != 'COMPLETE':
        task_log = TaskLog.objects.get(id=task_log.id)
        continue
    create_bills(workspace_id=workspace_id)
