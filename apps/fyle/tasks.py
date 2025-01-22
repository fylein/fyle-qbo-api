import logging
from datetime import datetime
from typing import Dict, List

from django.db import transaction
from fyle.platform.exceptions import InternalServerError, InvalidTokenError, RetryException
from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_integrations_platform_connector import PlatformConnector
from fyle_integrations_platform_connector.apis.expenses import Expenses as FyleExpenses

from apps.fyle.actions import create_generator_and_post_in_batches, mark_expenses_as_skipped
from apps.fyle.helpers import (
    construct_expense_filter_query,
    get_filter_credit_expenses,
    get_fund_source,
    get_source_account_type,
    handle_import_exception,
)
from apps.fyle.models import Expense, ExpenseFilter, ExpenseGroup, ExpenseGroupSettings
from apps.tasks.models import TaskLog, Error
from apps.workspaces.actions import export_to_qbo
from apps.workspaces.models import FyleCredential, LastExportDetail, Workspace, WorkspaceGeneralSettings
from fyle_qbo_api.logging_middleware import get_logger

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def get_task_log_and_fund_source(workspace_id: int):
    task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace_id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

    fund_source = get_fund_source(workspace_id)

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


def group_expenses_and_save(expenses: List[Dict], task_log: TaskLog, workspace: Workspace):
    expense_objects = Expense.create_expense_objects(expenses, workspace.id)
    expense_filters = ExpenseFilter.objects.filter(workspace_id=workspace.id).order_by('rank')
    filtered_expenses = expense_objects
    if expense_filters:
        expenses_object_ids = [expense_object.id for expense_object in expense_objects]
        final_query = construct_expense_filter_query(expense_filters)

        skipped_expense_ids = mark_expenses_as_skipped(final_query, expenses_object_ids, workspace)
        post_accounting_export_summary(workspace.fyle_org_id, workspace.id, skipped_expense_ids)

        filtered_expenses = Expense.objects.filter(
            is_skipped=False,
            id__in=expenses_object_ids,
            expensegroup__isnull=True,
            org_id=workspace.fyle_org_id
        )

    ExpenseGroup.create_expense_groups_by_report_id_fund_source(
        filtered_expenses, workspace.id
    )

    task_log.status = 'COMPLETE'
    task_log.save()


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

            filter_credit_expenses = get_filter_credit_expenses(expense_group_settings)

            expenses = []
            reimbursable_expense_count = 0
            settled_at, approved_at, last_paid_at = None, None, None

            if 'PERSONAL' in fund_source:
                if expense_group_settings.expense_state == 'PAYMENT_PROCESSING':
                    settled_at = last_synced_at

                if expense_group_settings.expense_state == 'PAID':
                    last_paid_at = last_synced_at

                expenses.extend(platform.expenses.get(source_account_type=['PERSONAL_CASH_ACCOUNT'], state=expense_group_settings.expense_state, settled_at=settled_at, filter_credit_expenses=filter_credit_expenses, last_paid_at=last_paid_at))

            if workspace.last_synced_at or expenses:
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

            if workspace.ccc_last_synced_at or len(expenses) != reimbursable_expense_count:
                workspace.ccc_last_synced_at = datetime.now()

            workspace.save()

            group_expenses_and_save(expenses, task_log, workspace)

    except FyleCredential.DoesNotExist:
        logger.info('Fyle credentials not found %s', workspace_id)
        task_log.detail = {'message': 'Fyle credentials do not exist in workspace'}
        task_log.status = 'FAILED'
        task_log.save()

    except RetryException:
        logger.info('Fyle Retry Exception occured in workspace_id %s', workspace_id)
        task_log.detail = {'message': 'Retrying task'}
        task_log.status = 'FATAL'
        task_log.save()

    except InvalidTokenError:
        logger.info('Invalid Token for Fyle')
        task_log.detail = {
            'message': 'Invalid Token for Fyle'
        }
        task_log.status = 'FAILED'
        task_log.save()

    except InternalServerError:
        logger.info('Fyle Internal Server Error occured in workspace_id: %s', workspace_id)
        task_log.detail = {
            'message': 'Fyle Internal Server Error occured'
        }
        task_log.status = 'FAILED'
        task_log.save()

    except Exception:
        handle_import_exception(task_log)


def sync_dimensions(fyle_credentials, is_export: bool = False):
    platform = PlatformConnector(fyle_credentials)
    platform.import_fyle_dimensions(is_export=is_export)
    if is_export:
        categories_count = platform.categories.get_count()

        categories_expense_attribute_count = ExpenseAttribute.objects.filter(
            attribute_type="CATEGORY", workspace_id=fyle_credentials.workspace_id, active=True
        ).count()

        if categories_count != categories_expense_attribute_count:
            platform.categories.sync()

        projects_count = platform.projects.get_count()

        projects_expense_attribute_count = ExpenseAttribute.objects.filter(
            attribute_type="PROJECT", workspace_id=fyle_credentials.workspace_id, active=True
        ).count()

        if projects_count != projects_expense_attribute_count:
            platform.projects.sync()


def post_accounting_export_summary(org_id: str, workspace_id: int, expense_ids, fund_source: str = None, is_failed: bool = False) -> None:
    """
    Post accounting export summary to Fyle
    :param org_id: org id
    :param workspace_id: workspace id
    :param fund_source: fund source
    :return: None
    """
    worker_logger = get_logger()
    # Iterate through all expenses which are not synced and post accounting export summary to Fyle in batches
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)
    filters = {
        'org_id': org_id,
        'id__in': expense_ids,
        'accounting_export_summary__synced': False
    }

    if fund_source:
        filters['fund_source'] = fund_source

    if is_failed:
        filters['accounting_export_summary__state'] = 'ERROR'

    expenses_count = Expense.objects.filter(**filters).count()

    accounting_export_summary_batches = []
    page_size = 200
    for offset in range(0, expenses_count, page_size):
        limit = offset + page_size
        paginated_expenses = Expense.objects.filter(**filters).order_by('id')[offset:limit]

        payload = []

        for expense in paginated_expenses:
            accounting_export_summary = expense.accounting_export_summary
            accounting_export_summary.pop('synced')
            payload.append(expense.accounting_export_summary)

        accounting_export_summary_batches.append(payload)

    worker_logger.info(
        'Posting accounting export summary to Fyle workspace_id: %s, payload: %s',
        workspace_id,
        accounting_export_summary_batches
    )
    create_generator_and_post_in_batches(accounting_export_summary_batches, platform, workspace_id)


def import_and_export_expenses(report_id: str, org_id: str) -> None:
    """
    Import and export expenses
    :param report_id: report id
    :param org_id: org id
    :return: None
    """
    workspace = Workspace.objects.get(fyle_org_id=org_id)
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace.id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace.id)

    try:
        with transaction.atomic():
            task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace.id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

            fund_source = get_fund_source(workspace.id)
            source_account_type = get_source_account_type(fund_source)
            filter_credit_expenses = get_filter_credit_expenses(expense_group_settings)

            platform = PlatformConnector(fyle_credentials)
            expenses = platform.expenses.get(
                source_account_type,
                filter_credit_expenses=filter_credit_expenses,
                report_id=report_id
            )

            group_expenses_and_save(expenses, task_log, workspace)

        # Export only selected expense groups
        expense_ids = Expense.objects.filter(report_id=report_id, org_id=org_id).values_list('id', flat=True)
        expense_groups = ExpenseGroup.objects.filter(expenses__id__in=[expense_ids], workspace_id=workspace.id).distinct('id').values('id')
        expense_group_ids = [expense_group['id'] for expense_group in expense_groups]

        if len(expense_group_ids):
            export_to_qbo(workspace.id, None, expense_group_ids, True)

    except WorkspaceGeneralSettings.DoesNotExist:
        logger.info('Workspace general settings not found %s', workspace.id)
        task_log.detail = {'message': 'Workspace general settings do not exist in workspace'}
        task_log.status = 'FAILED'
        task_log.save()

    except Exception:
        handle_import_exception(task_log)


def update_non_exported_expenses(data: Dict) -> None:
    """
    To update expenses not in COMPLETE, IN_PROGRESS state
    """
    expense_state = None
    org_id = data['org_id']
    expense_id = data['id']
    workspace = Workspace.objects.get(fyle_org_id = org_id)
    expense = Expense.objects.filter(workspace_id=workspace.id, expense_id=expense_id).first()

    if expense:
        if 'state' in expense.accounting_export_summary:
            expense_state = expense.accounting_export_summary['state']
        else:
            expense_state = 'NOT_EXPORTED'

        if expense_state and expense_state not in ['COMPLETE', 'IN_PROGRESS']:
            expense_obj = []
            expense_obj.append(data)
            expense_objects = FyleExpenses().construct_expense_object(expense_obj, expense.workspace_id)
            Expense.create_expense_objects(
                expense_objects, expense.workspace_id, skip_update=True
            )


def skip_expenses_pre_export(workspace_id: int, expense_group_ids: List[int]) -> None:
    """
    Skip expenses before export
    :param workspace_id: Workspace id
    :param expense_group_ids: Expense group ids
    :return: None
    """
    expense_filters = ExpenseFilter.objects.filter(workspace_id=workspace_id).order_by('rank')
    logger.info('Expense filters %s', expense_filters)
    if expense_filters:
        workspace = Workspace.objects.get(pk=workspace_id)
        filtered_expense_query = construct_expense_filter_query(expense_filters)

        # Get all expenses in the workspace that match filter conditions
        matching_expenses = Expense.objects.filter(
            filtered_expense_query,
            workspace_id=workspace_id,
            is_skipped=False
        ).values_list('id', flat=True)
        if matching_expenses:
            skipped_expenses = mark_expenses_as_skipped(filtered_expense_query, list(matching_expenses), workspace)
            if skipped_expenses:
                skipped_expense_ids = [expense.id for expense in skipped_expenses]

                # Find and clean up expense groups containing skipped expenses
                expense_groups = ExpenseGroup.objects.filter(expenses__id__in=skipped_expense_ids)

                for expense_group in expense_groups:
                    task_log = TaskLog.objects.filter(
                        workspace_id=workspace_id,
                        expense_group_id=expense_group.id
                    ).first()
                    if task_log:
                        logger.info('Deleting task log for expense group %s before export', expense_group.id)
                        task_log.delete()

                    error = Error.objects.filter(
                        workspace_id=workspace_id,
                        expense_group_id=expense_group.id
                    ).first()
                    if error:
                        logger.info('Deleting error for expense group %s before export', expense_group.id)
                        error.delete()

                    # Remove skipped expenses from the group
                    expense_group.expenses.remove(*skipped_expenses)
                    if not expense_group.expenses.exists():
                        logger.info('Deleting empty expense group %s before export', expense_group.id)
                        expense_group.delete()

                # Update last export details to reflect skipped expenses
                last_export_detail = LastExportDetail.objects.filter(workspace_id=workspace_id).first()
                if last_export_detail and last_export_detail.total_expense_groups_count:
                    deleted_groups_count = ExpenseGroup.objects.filter(
                        expenses__id__in=skipped_expense_ids
                    ).distinct().count()

                    if deleted_groups_count > 0:
                        last_export_detail.total_expense_groups_count = max(
                            0,
                            last_export_detail.total_expense_groups_count - deleted_groups_count
                        )
                        last_export_detail.successful_expense_groups_count = max(
                            0,
                            (last_export_detail.successful_expense_groups_count or 0) - deleted_groups_count
                        )
                        last_export_detail.save()

                        logger.info(
                            'Updated last export details for workspace %s: removed %s expense groups', 
                            workspace_id,
                            deleted_groups_count
                        )
