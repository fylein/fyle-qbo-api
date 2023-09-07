import logging
import traceback
from datetime import datetime
from typing import List

from django.db import transaction
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError, InternalServerError
from fyle_integrations_platform_connector import PlatformConnector

from apps.fyle.helpers import construct_expense_filter_query
from apps.fyle.models import Expense, ExpenseFilter, ExpenseGroup, ExpenseGroupSettings
from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings

from .actions import mark_expenses_as_skipped, mark_accounting_export_summary_as_synced
from .queue import async_post_accounting_export_summary

logger = logging.getLogger(__name__)
logger.level = logging.INFO

SOURCE_ACCOUNT_MAP = {'PERSONAL': 'PERSONAL_CASH_ACCOUNT', 'CCC': 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'}


def get_task_log_and_fund_source(workspace_id: int):
    task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace_id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    fund_source = []
    if general_settings.reimbursable_expenses_object:
        fund_source.append('PERSONAL')
    if general_settings.corporate_credit_card_expenses_object:
        fund_source.append('CCC')

    return task_log, fund_source


def create_expense_groups(workspace_id: int, fund_source: List[str], task_log: TaskLog):
    """
    Create expense groups
    :param task_log: Task log object
    :param workspace_id: workspace id
    :param fund_source: expense fund source
    :return: task log
    """

    async_create_expense_groups(workspace_id, fund_source, task_log)

    task_log.detail = {'message': 'Creating expense groups'}
    task_log.save()

    return task_log


def async_create_expense_groups(workspace_id: int, fund_source: List[str], task_log: TaskLog):
    try:
        with transaction.atomic():

            expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
            workspace = Workspace.objects.get(pk=workspace_id)
            ccc_last_synced_at = workspace.ccc_last_synced_at
            last_synced_at = workspace.last_synced_at
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

            filter_by_timestamp = []

            if last_synced_at:
                filter_by_timestamp.append('gte:{0}'.format(datetime.strftime(last_synced_at, '%Y-%m-%dT%H:%M:%S.000Z')))

            platform = PlatformConnector(fyle_credentials)

            source_account_type = []
            for source in fund_source:
                source_account_type.append(SOURCE_ACCOUNT_MAP[source])

            filter_credit_expenses = True
            if expense_group_settings.import_card_credits:
                filter_credit_expenses = False

            expenses = []
            reimbursable_expense_count = 0
            settled_at, approved_at, last_paid_at = None, None, None

            if 'PERSONAL' in fund_source:

                if expense_group_settings.expense_state == 'PAYMENT_PROCESSING':
                    settled_at = last_synced_at

                if expense_group_settings.expense_state == 'PAID':
                    last_paid_at = last_synced_at

                expenses.extend(platform.expenses.get(source_account_type=['PERSONAL_CASH_ACCOUNT'], state=expense_group_settings.expense_state, settled_at=settled_at, filter_credit_expenses=filter_credit_expenses, last_paid_at=last_paid_at))

            if expenses:
                workspace.last_synced_at = datetime.now()
                reimbursable_expense_count += len(expenses)

            settled_at, approved_at, last_paid_at = None, None, None

            if 'CCC' in fund_source:

                if expense_group_settings.ccc_expense_state == 'PAYMENT_PROCESSING':
                    settled_at = ccc_last_synced_at

                if expense_group_settings.ccc_expense_state == 'APPROVED':
                    approved_at = ccc_last_synced_at

                if expense_group_settings.ccc_expense_state == 'PAID':
                    last_paid_at = ccc_last_synced_at

                expenses.extend(
                    platform.expenses.get(
                        source_account_type=['PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'],
                        state=expense_group_settings.ccc_expense_state,
                        settled_at=settled_at,
                        approved_at=approved_at,
                        filter_credit_expenses=filter_credit_expenses,
                        last_paid_at=last_paid_at,
                    )
                )

            if len(expenses) != reimbursable_expense_count:
                workspace.ccc_last_synced_at = datetime.now()

            workspace.save()

            expense_objects = Expense.create_expense_objects(expenses, workspace_id)
            expense_filters = ExpenseFilter.objects.filter(workspace_id=workspace_id).order_by('rank')
            filtered_expenses = expense_objects
            if expense_filters:
                expenses_object_ids = [expense_object.id for expense_object in expense_objects]
                final_query = construct_expense_filter_query(expense_filters)
                mark_expenses_as_skipped(final_query, expenses_object_ids, workspace)
                async_post_accounting_export_summary(workspace.fyle_org_id, workspace_id)

                filtered_expenses = Expense.objects.filter(is_skipped=False, id__in=expenses_object_ids, expensegroup__isnull=True, org_id=workspace.fyle_org_id)

            ExpenseGroup.create_expense_groups_by_report_id_fund_source(filtered_expenses, workspace_id)

            task_log.status = 'COMPLETE'

            task_log.save()

    except FyleCredential.DoesNotExist:
        logger.info('Fyle credentials not found %s', workspace_id)
        task_log.detail = {'message': 'Fyle credentials do not exist in workspace'}
        task_log.status = 'FAILED'
        task_log.save()

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {'error': error}
        task_log.status = 'FATAL'
        task_log.save()
        logger.error('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)


def sync_dimensions(fyle_credentials):
    try:
        platform = PlatformConnector(fyle_credentials)
        platform.import_fyle_dimensions(import_taxes=True)
    except FyleInvalidTokenError:
        logger.info('Invalid Token for fyle')


def post_accounting_export_summary(org_id: str, workspace_id: int) -> None:
    """
    Post accounting export summary to Fyle
    :param org_id: org id
    :param workspace_id: workspace id
    :return: None
    """
    # Iterate through all expenses which are not synced and post accounting export summary to Fyle in batches
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)
    expenses_count = Expense.objects.filter(
        org_id=org_id, accounting_export_summary__synced=False
    ).count()

    page_size = 200
    for offset in range(0, expenses_count, page_size):
        limit = offset + page_size
        paginated_expenses = Expense.objects.filter(
            org_id=org_id, accounting_export_summary__synced=False
        )[offset:limit]

        payload = []

        for expense in paginated_expenses:
            accounting_export_summary = expense.accounting_export_summary
            accounting_export_summary.pop('synced')
            payload.append(expense.accounting_export_summary)

        if payload:
            try:
                platform.expenses.post_bulk_accounting_export_summary(payload)
                mark_accounting_export_summary_as_synced(paginated_expenses)
            except InternalServerError:
                logger.error(
                    'Internal server error while posting accounting export summary to Fyle workspace_id: %s',
                    workspace_id
                )
