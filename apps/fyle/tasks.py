from typing import List

from django.db import transaction

from apps.workspaces.models import FyleCredential
from apps.tasks.models import TaskLog

from .models import Expense, ExpenseGroup
from .utils import FyleConnector
from .serializers import ExpenseGroupSerializer


def create_expense_groups(workspace_id: int, state: List[str], export_non_reimbursable: bool, task_log: TaskLog):
    """
    Create expense groups
    :param workspace_id: workspace id
    :param state: expense state
    :param export_non_reimbursable: true / false
    :param task_log: Task log object
    :return:
    """
    try:
        with transaction.atomic():
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

            fyle_connector = FyleConnector(fyle_credentials.refresh_token)

            expenses = fyle_connector.get_expenses(
                state=state, export_non_reimbursable=export_non_reimbursable)

            expense_objects = Expense.create_expense_objects(expenses)

            expense_group_objects = ExpenseGroup.create_expense_groups_by_report_id(
                expense_objects, workspace_id
            )

            task_log.detail = ExpenseGroupSerializer(expense_group_objects, many=True).data

            task_log.status = 'COMPLETED'

            task_log.save(update_fields=['detail', 'status'])

    except FyleCredential.DoesNotExist:
        task_log.detail = {
            'message': 'Fyle credentials do not exist in workspace'
        }
        task_log.status = 'FAILED'
        task_log.save(update_fields=['detail', 'status'])
