import logging
from datetime import datetime, timedelta
from typing import Dict

from django_q.models import Schedule
from django_q.tasks import async_task

from apps.fyle.actions import update_failed_expenses
from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.utils import QBOConnector
from apps.tasks.models import TaskLog
from apps.workspaces.models import QBOCredential, Workspace

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def get_qbo_connection(query_params: Dict):
    org_id = query_params.get('org_id')

    workspace = Workspace.objects.get(fyle_org_id=org_id)
    workspace_id = workspace.id
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id=workspace.id)

    return QBOConnector(qbo_credentials, workspace_id=workspace_id)


def get_accounting_fields(query_params: Dict):
    qbo_connection = get_qbo_connection(query_params)
    resource_type = query_params.get('resource_type')

    return qbo_connection.get_accounting_fields(resource_type)


def get_exported_entry(query_params: Dict):
    qbo_connection = get_qbo_connection(query_params)
    resource_type = query_params.get('resource_type')
    internal_id = query_params.get('internal_id')

    return qbo_connection.get_exported_entry(resource_type, internal_id)


def re_export_stuck_exports():
    task_logs = TaskLog.objects.filter(
        status__in=['ENQUEUED', 'IN_PROGRESS'],
        updated_at__lt=datetime.now() - timedelta(minutes=60),
        expense_group_id__isnull=False
    )
    if task_logs.count() > 0:
        logger.info('Re-exporting stuck task_logs')
        logger.info('%s stuck task_logs found', task_logs.count())
        workspace_ids = task_logs.values_list('workspace_id', flat=True).distinct()

        expense_group_ids = task_logs.values_list('expense_group', flat=True)
        logger.info('Re-exporting Expense Group IDs: %s', expense_group_ids)
        expense_groups = ExpenseGroup.objects.filter(id__in=expense_group_ids)

        expenses = []
        for expense_group in expense_groups:
            expenses.extend(expense_group.expenses.all())

        workspace_ids_list = list(workspace_ids)

        task_logs.update(status='FAILED', updated_at=datetime.now())
        update_failed_expenses(expenses, True)

        workspaces = Workspace.objects.filter(id__in=workspace_ids_list)

        schedules = Schedule.objects.filter(
            args__in=[str(workspace.id) for workspace in workspaces],
            func='apps.workspaces.tasks.run_sync_schedule'
        )
        for workspace in workspaces:
            schedule = schedules.filter(args=str(workspace.id)).first()
            # If schedule exist and it's within 1 hour, need not trigger it immediately
            if not (schedule and schedule.next_run < datetime.now(tz=schedule.next_run.tzinfo) + timedelta(minutes=60)):
                async_task('apps.workspaces.tasks.run_sync_schedule', workspace.id)
