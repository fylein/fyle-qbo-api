import json
import logging
import traceback

from qbosdk.exceptions import InvalidTokenError, WrongParamsError

from apps.fyle.models import ExpenseGroup
from apps.fyle.helpers import update_failed_expenses
from apps.quickbooks_online.actions import update_last_export_details
from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import FyleCredential, QBOCredential
from fyle_qbo_api.exceptions import BulkError

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_quickbooks_error(exception, expense_group: ExpenseGroup, task_log: TaskLog, export_type: str):
    logger.info(exception.response)
    response = json.loads(exception.response)
    if 'Fault' not in response:
        logger.info(response)
        if 'error' in response and response['error'] == 'invalid_grant':
            qbo_credentials: QBOCredential = QBOCredential.objects.filter(workspace_id=expense_group.workspace_id).first()
            if qbo_credentials:
                qbo_credentials.is_expired = True
                qbo_credentials.refresh_token = None
                qbo_credentials.save()
        errors = response
    else:
        quickbooks_errors = response['Fault']['Error']

        error_msg = 'Failed to create {0}'.format(export_type)
        errors = []

        for error in quickbooks_errors:
            error = {
                'expense_group_id': expense_group.id,
                'type': '{0} / {1}'.format(response['Fault']['type'], error['code']),
                'short_description': error['Message'] if error['Message'] else '{0} error'.format(export_type),
                'long_description': error['Detail'] if error['Detail'] else error_msg,
            }
            errors.append(error)

            if export_type != 'Bill Payment':
                Error.objects.update_or_create(workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'error_title': error['type'], 'type': 'QBO_ERROR', 'error_detail': error['long_description'], 'is_resolved': False})

    task_log.status = 'FAILED'
    task_log.detail = None
    task_log.quickbooks_errors = errors
    task_log.save()


def handle_qbo_exceptions(bill_payment=False):
    def decorator(func):
        def new_fn(*args):
            if not bill_payment:
                expense_group = args[0]
                task_log_id = args[1]
                task_log = TaskLog.objects.get(id=task_log_id)
            else:
                expense_group = args[0].expense_group
                task_log = args[2]
            try:
                return func(*args)
            except (FyleCredential.DoesNotExist, InvalidTokenError):
                logger.info('Fyle credentials not found %s', expense_group.workspace_id)
                task_log.detail = {'message': 'Fyle credentials do not exist in workspace'}
                task_log.status = 'FAILED'

                task_log.save()

                if not bill_payment:
                    update_failed_expenses(expense_group.expenses.all(), True)

            except QBOCredential.DoesNotExist:
                logger.info('QBO Account not connected / token expired for workspace_id %s / expense group %s', expense_group.workspace_id, expense_group.id)
                detail = {'expense_group_id': expense_group.id, 'message': 'QBO Account not connected / token expired'}
                task_log.status = 'FAILED'
                task_log.detail = detail

                task_log.save()

                if not bill_payment:
                    update_failed_expenses(expense_group.expenses.all(), True)

            except WrongParamsError as exception:
                handle_quickbooks_error(exception, expense_group, task_log, 'Bill')

                if not bill_payment:
                    update_failed_expenses(expense_group.expenses.all(), False)

            except BulkError as exception:
                logger.info(exception.response)
                detail = exception.response
                task_log.status = 'FAILED'
                task_log.detail = detail

                task_log.save()

                if not bill_payment:
                    update_failed_expenses(expense_group.expenses.all(), True)

            except Exception as error:
                error = traceback.format_exc()
                task_log.detail = {'error': error}
                task_log.status = 'FATAL'

                task_log.save()
                logger.error('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)

                if not bill_payment:
                    update_failed_expenses(expense_group.expenses.all(), True)

            if len(args) > 2 and args[2] == True and not bill_payment:
                update_last_export_details(expense_group.workspace_id)

        return new_fn

    return decorator
