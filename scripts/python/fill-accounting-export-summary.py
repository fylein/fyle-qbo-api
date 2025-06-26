from datetime import datetime

from django.conf import settings
from django.db.models import Q

from apps.fyle.actions import __bulk_update_expenses
from apps.fyle.helpers import get_updated_accounting_export_summary
from apps.fyle.models import Expense
from apps.quickbooks_online.helpers import generate_export_type_and_id
from apps.tasks.models import TaskLog
from apps.workspaces.models import Workspace

# PLEASE RUN sql/scripts/022-fill-skipped-accounting-export-summary.sql BEFORE RUNNING THIS SCRIPT


export_types = ['CREATING_BILL', 'CREATING_EXPENSE', 'CREATING_CHECK', 'CREATING_CREDIT_CARD_PURCHASE', 'CREATING_JOURNAL_ENTRY', 'CREATING_CREDIT_CARD_CREDIT', 'CREATING_DEBIT_CARD_EXPENSE']
task_statuses = ['COMPLETE', 'FAILED', 'FATAL']


# We'll handle all COMPLETE, ERROR expenses in this script
workspaces = Workspace.objects.filter(
    ~Q(name__icontains='fyle for') & ~Q(name__icontains='test')
)

start_time = datetime.now()
number_of_expenses_without_accounting_export_summary = Expense.objects.filter(
    accounting_export_summary__state__isnull=True
).count()
print('Number of expenses without accounting export summary - {}'.format(number_of_expenses_without_accounting_export_summary))
for workspace in workspaces:
    task_logs_count = TaskLog.objects.filter(
        type__in=export_types,
        workspace_id=workspace.id,
        status__in=task_statuses
    ).count()
    print('Updating summary from workspace - {} with ID - {}'.format(workspace.name, workspace.id))
    print('Number of task logs to be updated - {}'.format(task_logs_count))
    page_size = 200
    for offset in range(0, task_logs_count, page_size):
        expense_to_be_updated = []
        limit = offset + page_size
        paginated_task_logs = TaskLog.objects.filter(
            type__in=export_types,
            workspace_id=workspace.id,
            status__in=task_statuses
        )[offset:limit]
        for task_log in paginated_task_logs:
            expense_group = task_log.expense_group
            state = 'ERROR' if task_log.status == 'FAILED' or task_log.status == 'FATAL' else 'COMPLETE'
            error_type = None
            url = None
            if task_log.status == 'FAILED' or task_log.status == 'FATAL':
                error_type = 'ACCOUNTING_INTEGRATION_ERROR' if task_log.quickbooks_errors else 'MAPPING'
                url = '{}/workspaces/main/dashboard'.format(settings.QBO_INTEGRATION_APP_URL)
            else:
                export_type, export_id = generate_export_type_and_id(expense_group)
                url = '{qbo_app_url}/app/{export_type}?txnId={export_id}'.format(
                    qbo_app_url=settings.QBO_APP_URL,
                    export_type=export_type,
                    export_id=export_id
                )
            for expense in expense_group.expenses.filter(accounting_export_summary__state__isnull=True):
                expense_to_be_updated.append(
                    Expense(
                        id=expense.id,
                        accounting_export_summary=get_updated_accounting_export_summary(
                            expense.expense_id,
                            state,
                            error_type,
                            url,
                            False
                        )
                    )
                )
        print('Updating {} expenses in batches of 50'.format(len(expense_to_be_updated)))
        __bulk_update_expenses(expense_to_be_updated)


number_of_expenses_without_accounting_export_summary = Expense.objects.filter(
    accounting_export_summary__state__isnull=True
).count()
print('Number of expenses without accounting export summary - {}'.format(number_of_expenses_without_accounting_export_summary))
end_time = datetime.now()
print('Time taken - {}'.format(end_time - start_time))
