import logging
import json
import traceback
from typing import List

from django.conf import settings
from django.db import transaction

from qbosdk.exceptions import WrongParamsError

from fyle_jobs import FyleJobsSDK
from fyle_qbo_api.exceptions import BulkError

from apps.fyle.utils import FyleConnector
from apps.fyle.models import ExpenseGroup
from apps.tasks.models import TaskLog
from apps.mappings.models import EmployeeMapping, GeneralMapping, CategoryMapping
from apps.workspaces.models import QBOCredential, FyleCredential

from .models import Bill, BillLineitem, QuickbooksCheck, CheckLineitem
from .utils import QBOConnector

logger = logging.getLogger(__name__)


def schedule_bills_creation(workspace_id: int, expense_group_ids: List[str], user):
    """
    Schedule bills creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :param user: user email
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, id__in=expense_group_ids, bill__id__isnull=True
        ).all()
    else:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, bill__id__isnull=True
        ).all()

    fyle_credentials = FyleCredential.objects.get(
        workspace_id=workspace_id)
    fyle_connector = FyleConnector(fyle_credentials.refresh_token)
    fyle_sdk_connection = fyle_connector.connection
    jobs = FyleJobsSDK(settings.FYLE_JOBS_URL, fyle_sdk_connection)

    for expense_group in expense_groups:
        task_log, _ = TaskLog.objects.update_or_create(
            workspace_id=expense_group.workspace_id,
            expense_group=expense_group,
            defaults={
                'status': 'IN_PROGRESS',
                'type': 'CREATING_BILL'
            }
        )
        created_job = jobs.trigger_now(
            callback_url='{0}{1}'.format(settings.API_URL, '/workspaces/{0}/qbo/bills/'.format(workspace_id)),
            callback_method='POST', object_id=task_log.id, payload={
                'expense_group_id': expense_group.id,
                'task_log_id': task_log.id
            }, job_description='Create Bill: Workspace id - {0}, user - {1}, expense group id - {2}'.format(
                workspace_id, user, expense_group.id
            )
        )
        task_log.task_id = created_job['id']
        task_log.save()


def create_bill(expense_group, task_log):
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
        logger.exception(
            'QBO Credentials not found for workspace_id %s / expense group %s',
            expense_group.id,
            expense_group.workspace_id
        )
        detail = {
            'expense_group_id': expense_group.id,
            'message': 'QBO Account not connected'
        }
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except BulkError as exception:
        logger.error(exception.response)
        detail = exception.response
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except WrongParamsError as exception:
        logger.error(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save(update_fields=['detail', 'status'])
        logger.exception('Something unexpected happened workspace_id: %s\n%s', task_log.workspace_id, error)


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
            'type': 'General Mapping',
            'message': 'General mapping not found'
        })

    try:
        EmployeeMapping.objects.get(
            employee_email=expense_group.description.get('employee_email'),
            workspace_id=expense_group.workspace_id
        )
    except EmployeeMapping.DoesNotExist:
        bulk_errors.append({
            'row': None,
            'expense_group_id': expense_group.id,
            'value': expense_group.description.get('employee_email'),
            'type': 'Employee Mapping',
            'message': 'Employee mapping not found'
        })

    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        account = CategoryMapping.objects.filter(category=lineitem.category,
                                                 sub_category=lineitem.sub_category,
                                                 workspace_id=expense_group.workspace_id).first()
        if not account:
            bulk_errors.append({
                'row': row,
                'expense_group_id': expense_group.id,
                'value': '{0} / {1}'.format(lineitem.category, lineitem.sub_category),
                'type': 'Category Mapping',
                'message': 'Category Mapping not found'
            })

        row = row + 1

    if bulk_errors:
        raise BulkError('Mappings are missing', bulk_errors)


def schedule_checks_creation(workspace_id: int, expense_group_ids: List[str], user):
    """
    Schedule checks creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :param user: user email
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, id__in=expense_group_ids, quickbookscheck__id__isnull=True
        ).all()
    else:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, quickbookscheck__id__isnull=True
        ).all()

    fyle_credentials = FyleCredential.objects.get(
        workspace_id=workspace_id)
    fyle_connector = FyleConnector(fyle_credentials.refresh_token)
    fyle_sdk_connection = fyle_connector.connection
    jobs = FyleJobsSDK(settings.FYLE_JOBS_URL, fyle_sdk_connection)

    for expense_group in expense_groups:
        task_log, _ = TaskLog.objects.update_or_create(
            workspace_id=expense_group.workspace_id,
            expense_group=expense_group,
            defaults={
                'status': 'IN_PROGRESS',
                'type': 'CREATING_CHECK'
            }
        )
        created_job = jobs.trigger_now(
            callback_url='{0}{1}'.format(settings.API_URL, '/workspaces/{0}/qbo/checks/'.format(workspace_id)),
            callback_method='POST', object_id=task_log.id, payload={
                'expense_group_id': expense_group.id,
                'task_log_id': task_log.id
            }, job_description='Create Check: Workspace id - {0}, user - {1}, expense group id - {2}'.format(
                workspace_id, user, expense_group.id
            )
        )
        task_log.task_id = created_job['id']
        task_log.save()


def create_check(expense_group, task_log):
    try:
        with transaction.atomic():
            __validate_expense_group(expense_group)

            check_object = QuickbooksCheck.create_check(expense_group)

            check_line_item_objects = CheckLineitem.create_check_lineitems(expense_group)

            qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

            qbo_connection = QBOConnector(qbo_credentials)

            created_check = qbo_connection.post_check(check_object, check_line_item_objects)

            task_log.detail = created_check
            task_log.quickbooks_check = check_object
            task_log.status = 'COMPLETE'

            task_log.save(update_fields=['detail', 'quickbooks_check', 'status'])

    except QBOCredential.DoesNotExist:
        logger.exception(
            'QBO Credentials not found for workspace_id %s / expense group %s',
            expense_group.id,
            expense_group.workspace_id
        )
        detail = {
            'expense_group_id': expense_group.id,
            'message': 'QBO Account not connected'
        }
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except BulkError as exception:
        logger.error(exception.response)
        detail = exception.response
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except WrongParamsError as exception:
        logger.error(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save(update_fields=['detail', 'status'])
        logger.exception('Something unexpected happened workspace_id: %s\n%s', task_log.workspace_id, error)
