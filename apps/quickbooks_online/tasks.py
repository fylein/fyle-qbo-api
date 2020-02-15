import json

from django.db import transaction

from qbosdk.exceptions import WrongParamsError

from fyle_qbo_api.exceptions import BulkError

from apps.fyle.models import ExpenseGroup
from apps.tasks.models import TaskLog
from apps.mappings.models import EmployeeMapping, GeneralMapping, CategoryMapping
from apps.workspaces.models import QBOCredential

from .models import Bill, BillLineitem
from .utils import QBOConnector


def create_bill(expense_group: ExpenseGroup, task_log: TaskLog):
    """
    Create bill
    :param task_log: Task log
    :param expense_group: expense group
    """

    try:
        with transaction.atomic():
            __validate_expense_group(expense_group)

            bill_object = Bill.create_bill(expense_group)

            bill_lineitems_objects = BillLineitem.create_bill_lineitems(expense_group)

            qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

            qbo_connection = QBOConnector(qbo_credentials)

            created_bill = qbo_connection.post_bill(bill_object, bill_lineitems_objects)

            task_log.detail = created_bill
            task_log.bill = bill_object
            task_log.status = 'COMPLETE'

            task_log.save(update_fields=['detail', 'bill', 'status'])

    except QBOCredential.DoesNotExist:
        detail = {
            'expense_group_id': expense_group.id,
            'message': 'QBO Account not connected'
        }
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except BulkError as e:
        detail = e.response
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except WrongParamsError as e:
        detail = json.loads(e.response)
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])


def __validate_expense_group(expense_group: ExpenseGroup):
    bulk_errors = []
    row = 0
    try:
        GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
    except GeneralMapping.DoesNotExist:
        bulk_errors.append({
            'row': None,
            'expense_group_id': expense_group.id,
            'value': 'bank account',
            'message': 'Employee mappings not found'
        })

    try:
        EmployeeMapping.objects.get(employee_email=expense_group.description.get('employee_email'))
    except EmployeeMapping.DoesNotExist:
        bulk_errors.append({
            'row': None,
            'expense_group_id': expense_group.id,
            'value': expense_group.description.get('employee_email'),
            'message': 'Employee mappings not found'
        })

    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        account = CategoryMapping.objects.filter(category=lineitem.category,
                                                 sub_category=lineitem.sub_category).first()
        if not account:
            bulk_errors.append({
                'row': row,
                'expense_group_id': expense_group.id,
                'value': '{0} / {1}'.format(lineitem.category, lineitem.sub_category),
                'message': 'Category Mapping not found'
            })

        row = row + 1

    if bulk_errors:
        raise BulkError('Mappings are missing', bulk_errors)
