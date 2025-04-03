import json
import logging
import traceback

from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError
from qbosdk.exceptions import InternalServerError, InvalidTokenError, WrongParamsError

from apps.fyle.actions import post_accounting_export_summary, update_failed_expenses
from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.actions import update_last_export_details
from apps.quickbooks_online.errors.helpers import error_matcher, get_entity_values, replace_destination_id_with_values
from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import FyleCredential, QBOCredential
from fyle_qbo_api.exceptions import BulkError
from fyle_qbo_api.utils import invalidate_qbo_credentials

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_qbo_invalid_token_error(expense_group: ExpenseGroup) -> None:
    """
    Handles the case when QuickBooks Online token expires by creating
    Args:
        expense_group (ExpenseGroup): The expense group for which the token error occurred
    """
    logger.info(
        'Creating/updating QBO token error for workspace %s and expense group %s',
        expense_group.workspace_id,
        expense_group.id
    )

    existing_error = Error.objects.filter(
        workspace_id=expense_group.workspace_id,
        error_title='QuickBooks Online Connection Expired',
        is_resolved=False
    ).first()

    if not existing_error:
        Error.objects.update_or_create(
            workspace_id=expense_group.workspace_id,
            expense_group=expense_group,
            defaults={
                'error_title': 'QuickBooks Online Connection Expired',
                'type': 'QBO_ERROR',
                'error_detail': 'Your QuickBooks Online connection had expired during the previous export. Please click \'Export\' to retry exporting your expenses.',
                'is_resolved': False,
                'is_parsed': False,
                'attribute_type': None,
                'article_link': None
            })


def handle_quickbooks_error(exception, expense_group: ExpenseGroup, task_log: TaskLog, export_type: str):
    logger.info(exception.response)
    response = json.loads(exception.response)
    if 'Fault' not in response:
        logger.info(response)
        if 'error' in response and response['error'] == 'invalid_grant':
            invalidate_qbo_credentials(expense_group.workspace_id)

        errors = response
    else:
        quickbooks_errors = response['Fault']['Error']

        error_msg = 'Failed to create {0}'.format(export_type)
        errors = []

        for error in quickbooks_errors:
            article_link = None
            attribute_type = None
            is_parsed = False
            error = {
                'expense_group_id': expense_group.id,
                'type': '{0} / {1}'.format(response['Fault']['type'], error['code']),
                'short_description': error['Message'] if error['Message'] else '{0} error'.format(export_type),
                'long_description': error['Detail'] if error['Detail'] else error_msg,
            }
            errors.append(error)

            if export_type != 'Bill Payment':
                error_msg = error['long_description']
                error_dict = error_matcher(error_msg)
                if error_dict:
                    error_entity_values = get_entity_values(error_dict, expense_group.workspace_id)
                    if error_entity_values:
                        error_msg = replace_destination_id_with_values(error_msg, error_entity_values)
                        is_parsed = True
                        article_link = error_dict['article_link']
                        attribute_type = error_dict['attribute_type']

                error, created = Error.objects.update_or_create(
                    workspace_id=expense_group.workspace_id,
                    expense_group=expense_group,
                    defaults={
                        'error_title': error['type'],
                        'type': 'QBO_ERROR',
                        'error_detail': error_msg,
                        'is_resolved': False,
                        'is_parsed': is_parsed,
                        'attribute_type': attribute_type,
                        'article_link': article_link
                    })
                error.increase_repetition_count_by_one(created)

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
            except (FyleCredential.DoesNotExist, FyleInvalidTokenError):
                logger.info('Fyle credentials not found %s', expense_group.workspace_id)
                task_log.detail = {'message': 'Fyle credentials do not exist in workspace'}
                task_log.status = 'FAILED'

                task_log.save()

                if not bill_payment:
                    update_failed_expenses(expense_group.expenses.all(), True)

            except (QBOCredential.DoesNotExist, InvalidTokenError):
                logger.info('QBO Account not connected / token expired for workspace_id %s / expense group %s', expense_group.workspace_id, expense_group.id)
                detail = {'expense_group_id': expense_group.id, 'message': 'QBO Account not connected / token expired'}
                task_log.status = 'FAILED'
                task_log.detail = detail
                invalidate_qbo_credentials(expense_group.workspace_id)
                handle_qbo_invalid_token_error(expense_group)
                task_log.save()

                if not bill_payment:
                    update_failed_expenses(expense_group.expenses.all(), False)

            except WrongParamsError as exception:
                handle_quickbooks_error(exception, expense_group, task_log, 'Bill')

                if not bill_payment:
                    update_failed_expenses(expense_group.expenses.all(), False)

            except InternalServerError as error:
                task_log.detail = {'error': error}
                task_log.status = 'FAILED'

                task_log.save()
                logger.error('Internal Server Error for workspace_id: %s %s', task_log.workspace_id, task_log.detail)

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

            post_accounting_export_summary(expense_group.workspace.fyle_org_id, expense_group.workspace_id, [expense.id for expense in expense_group.expenses.all()], expense_group.fund_source, True)
            if len(args) > 2 and args[2] == True and not bill_payment:
                update_last_export_details(expense_group.workspace_id)

        return new_fn

    return decorator
