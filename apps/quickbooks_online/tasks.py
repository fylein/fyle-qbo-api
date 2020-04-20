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

from .models import Bill, BillLineitem, Cheque, ChequeLineitem, CreditCardPurchase, CreditCardPurchaseLineitem,\
    JournalEntry, JournalEntryLineitem
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


def schedule_cheques_creation(workspace_id: int, expense_group_ids: List[str], user: str):
    """
    Schedule cheque creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :param user: user email
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, id__in=expense_group_ids, cheque__id__isnull=True
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


def create_cheque(expense_group, task_log):
    try:
        with transaction.atomic():
            __validate_expense_group(expense_group)

            cheque_object = Cheque.create_cheque(expense_group)

            cheque_line_item_objects = ChequeLineitem.create_cheque_lineitems(expense_group)

            qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

            qbo_connection = QBOConnector(qbo_credentials)

            created_cheque = qbo_connection.post_cheque(cheque_object, cheque_line_item_objects)

            task_log.detail = created_cheque
            task_log.cheque = cheque_object
            task_log.status = 'COMPLETE'

            task_log.save(update_fields=['detail', 'cheque', 'status'])

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


def schedule_credit_card_purchase_creation(workspace_id: int, expense_group_ids: List[str], user: str):
    """
    Schedule credit card purchase creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :param user: user email
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, id__in=expense_group_ids, creditcardpurchase__id__isnull=True
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
                    'type': 'CREATING_CREDIT_CARD_PURCHASE'
                }
            )
            created_job = jobs.trigger_now(
                callback_url='{0}{1}'.format(settings.API_URL, '/workspaces/{0}/qbo/credit_card_purchases/'.format(
                    workspace_id
                )),
                callback_method='POST', object_id=task_log.id, payload={
                    'expense_group_id': expense_group.id,
                    'task_log_id': task_log.id
                }, job_description=
                'Create Credit Card Purchase: Workspace id - {0}, user - {1}, expense group id - {2}'.format(
                    workspace_id, user, expense_group.id
                )
            )
            task_log.task_id = created_job['id']
            task_log.save()


def create_credit_card_purchase(expense_group, task_log):
    try:
        with transaction.atomic():
            __validate_expense_group(expense_group)

            credit_card_purchase_object = CreditCardPurchase.create_credit_card_purchase(expense_group)

            credit_card_purchase_lineitems_objects = CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(
                expense_group
            )
            qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

            qbo_connection = QBOConnector(qbo_credentials)

            created_credit_card_purchase = qbo_connection.post_credit_card_purchase(
                credit_card_purchase_object, credit_card_purchase_lineitems_objects
            )

            task_log.detail = created_credit_card_purchase
            task_log.credit_card_purchase = credit_card_purchase_object
            task_log.status = 'COMPLETE'

            task_log.save(update_fields=['detail', 'credit_card_purchase', 'status'])

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


def schedule_journal_entry_creation(workspace_id: int, expense_group_ids: List[str], user: str):
    """
    Schedule journal_entry creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :param user: user email
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, id__in=expense_group_ids, journalentry__id__isnull=True
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
                    'type': 'CREATING_JOURNAL_ENTRY'
                }
            )
            created_job = jobs.trigger_now(
                callback_url='{0}{1}'.format(settings.API_URL, '/workspaces/{0}/qbo/journal_entries/'.format(
                    workspace_id)),
                callback_method='POST', object_id=task_log.id, payload={
                    'expense_group_id': expense_group.id,
                    'task_log_id': task_log.id
                },
                job_description='Create Journal Entry: Workspace id - {0}, user - {1}, expense group id - {2}'.format(
                    workspace_id, user, expense_group.id
                )
            )
            task_log.task_id = created_job['id']
            task_log.save()


def create_journal_entry(expense_group, task_log):
    try:
        with transaction.atomic():
            __validate_expense_group(expense_group)

            journal_entry_object = JournalEntry.create_journal_entry(expense_group)

            journal_entry_lineitems_objects = JournalEntryLineitem.create_journal_entry_lineitems(
                expense_group
            )

            qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

            qbo_connection = QBOConnector(qbo_credentials)

            created_journal_entry = qbo_connection.post_journal_entry(journal_entry_object,
                                                                      journal_entry_lineitems_objects)

            task_log.detail = created_journal_entry
            task_log.journal_entry = journal_entry_object
            task_log.status = 'COMPLETE'

            task_log.save(update_fields=['detail', 'journal_entry', 'status'])

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
