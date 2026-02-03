import hashlib
import logging
import traceback
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from django.db import transaction
from django.db.models import Count, Q
from django_q.models import Schedule
from django_q.tasks import async_task, schedule
from fyle.platform.exceptions import (
    RetryException,
    InternalServerError,
    ExpiredTokenError as FyleExpiredTokenError,
    InvalidTokenError as FyleInvalidTokenError
)
from fyle_accounting_library.fyle_platform.branding import feature_configuration
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_accounting_library.fyle_platform.helpers import filter_expenses_based_on_state, get_expense_import_states
from fyle_accounting_mappings.models import ExpenseAttribute, Mapping
from fyle_integrations_platform_connector import PlatformConnector

from fyle_accounting_library.system_comments.models import SystemComment

from apps.fyle.actions import mark_expenses_as_skipped, post_accounting_export_summary
from apps.fyle.helpers import (
    construct_expense_filter_query,
    get_filter_credit_expenses,
    get_fund_source,
    get_source_account_type,
    handle_import_exception,
    update_task_log_post_import,
)
from apps.fyle.models import SOURCE_ACCOUNT_MAP as EXPENSE_SOURCE_ACCOUNT_MAP
from apps.fyle.models import Expense, ExpenseFilter, ExpenseGroup, ExpenseGroupSettings
from apps.tasks.models import Error, TaskLog
from apps.workspaces.actions import export_to_qbo
from apps.workspaces.enums import SystemCommentEntityTypeEnum, SystemCommentIntentEnum, SystemCommentReasonEnum, SystemCommentSourceEnum
from apps.workspaces.models import FyleCredential, LastExportDetail, Workspace, WorkspaceGeneralSettings, WorkspaceSchedule
from apps.workspaces.system_comments import add_system_comment

logger = logging.getLogger(__name__)
logger.level = logging.INFO

SOURCE_ACCOUNT_MAP = {
    'PERSONAL': 'PERSONAL_CASH_ACCOUNT',
    'CCC': 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'
}


def get_task_log_and_fund_source(workspace_id: int):
    task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace_id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

    fund_source = get_fund_source(workspace_id)

    return task_log, fund_source


def schedule_expense_group_creation(workspace_id: int):
    """
    Schedule Expense group creation
    :param workspace_id: Workspace id
    :param user: User email
    :return: None
    """
    task_log, fund_source = get_task_log_and_fund_source(workspace_id)

    # Use Django Q's async_task function to schedule the task
    # This maintains compatibility with existing code that might call this function
    async_task('apps.fyle.tasks.create_expense_groups', workspace_id, fund_source, task_log)


def skip_expenses_and_post_accounting_export_summary(expense_ids: List[int], workspace: Workspace, q_filters: Q = None):
    """
    Skip expenses and post accounting export summary
    :param expense_ids: List of expense ids
    :param workspace: Workspace object
    :param q_filters: Additional query filters
    :return: None
    """
    if not q_filters:
        q_filters = Q()

    skipped_expenses = mark_expenses_as_skipped(q_filters, expense_ids, workspace)
    if skipped_expenses:
        try:
            post_accounting_export_summary(workspace_id=workspace.id, expense_ids=[expense.id for expense in skipped_expenses])
        except Exception:
            logger.exception('Error posting accounting export summary for workspace_id: %s', workspace.id)


def group_expenses_and_save(
    expenses: List[Dict],
    task_log: TaskLog | None,
    workspace: Workspace,
    imported_from: ExpenseImportSourceEnum = None,
    filter_credit_expenses: bool = False,
    system_comments: list = None
):
    """
    Group expenses and save them as expense groups
    :param expenses: List of expenses
    :param task_log: Task log object
    :param workspace: Workspace object
    :param imported_from: Imported from
    :param filter_credit_expenses: Filter credit expenses
    :param system_comments: Optional list to collect system comment data
    """
    expense_filters = ExpenseFilter.objects.filter(workspace_id=workspace.id).order_by('rank')
    configuration: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace.id)

    expense_objects = Expense.create_expense_objects(expenses, workspace.id, imported_from=imported_from)

    # Step 1: Mark negative expenses as skipped if filter_credit_expenses is True
    if filter_credit_expenses:
        negative_expense_ids = [e.id for e in expense_objects if e.amount <= 0 and not e.is_skipped]
        if negative_expense_ids:
            for expense_id in negative_expense_ids:
                add_system_comment(
                    system_comments=system_comments,
                    source=SystemCommentSourceEnum.GROUP_EXPENSES_AND_SAVE,
                    intent=SystemCommentIntentEnum.SKIP_EXPENSE,
                    entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                    workspace_id=workspace.id,
                    entity_id=expense_id,
                    reason=SystemCommentReasonEnum.NEGATIVE_EXPENSE_SKIPPED
                )
            expense_objects = [e for e in expense_objects if e.id not in negative_expense_ids]
            skip_expenses_and_post_accounting_export_summary(negative_expense_ids, workspace)

    # Skip reimbursable expenses if reimbursable expense settings is not configured
    if not configuration.reimbursable_expenses_object:
        reimbursable_expense_ids = [e.id for e in expense_objects if e.fund_source == 'PERSONAL']

        if reimbursable_expense_ids:
            for expense_id in reimbursable_expense_ids:
                add_system_comment(
                    system_comments=system_comments,
                    source=SystemCommentSourceEnum.GROUP_EXPENSES_AND_SAVE,
                    intent=SystemCommentIntentEnum.SKIP_EXPENSE,
                    entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                    workspace_id=workspace.id,
                    entity_id=expense_id,
                    reason=SystemCommentReasonEnum.REIMBURSABLE_EXPENSE_NOT_CONFIGURED
                )
            expense_objects = [e for e in expense_objects if e.id not in reimbursable_expense_ids]
            skip_expenses_and_post_accounting_export_summary(reimbursable_expense_ids, workspace)

    # Skip corporate credit card expenses if corporate credit card expense settings is not configured
    if not configuration.corporate_credit_card_expenses_object:
        ccc_expense_ids = [e.id for e in expense_objects if e.fund_source == 'CCC']

        if ccc_expense_ids:
            for expense_id in ccc_expense_ids:
                add_system_comment(
                    system_comments=system_comments,
                    source=SystemCommentSourceEnum.GROUP_EXPENSES_AND_SAVE,
                    intent=SystemCommentIntentEnum.SKIP_EXPENSE,
                    entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                    workspace_id=workspace.id,
                    entity_id=expense_id,
                    reason=SystemCommentReasonEnum.CCC_EXPENSE_NOT_CONFIGURED
                )
            expense_objects = [e for e in expense_objects if e.id not in ccc_expense_ids]
            skip_expenses_and_post_accounting_export_summary(ccc_expense_ids, workspace)

    filtered_expenses = expense_objects

    if expense_filters:
        expenses_object_ids = [expense_object.id for expense_object in expense_objects]
        final_query = construct_expense_filter_query(expense_filters)
        skipped_expenses = mark_expenses_as_skipped(final_query, expenses_object_ids, workspace)
        if skipped_expenses:
            for expense in skipped_expenses:
                add_system_comment(
                    system_comments=system_comments,
                    source=SystemCommentSourceEnum.GROUP_EXPENSES_AND_SAVE,
                    intent=SystemCommentIntentEnum.SKIP_EXPENSE,
                    entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                    workspace_id=workspace.id,
                    entity_id=expense.id,
                    reason=SystemCommentReasonEnum.EXPENSE_SKIPPED_AFTER_IMPORT
                )
            try:
                post_accounting_export_summary(workspace_id=workspace.id, expense_ids=[expense.id for expense in skipped_expenses])
            except Exception:
                logger.error('Error posting accounting export summary for workspace_id: %s', workspace.id)

        filtered_expenses = Expense.objects.filter(
            is_skipped=False,
            id__in=expenses_object_ids,
            expensegroup__isnull=True,
            org_id=workspace.fyle_org_id
        )

    expense_group_objects, skipped_expense_ids = ExpenseGroup.create_expense_groups_by_report_id_fund_source(
        filtered_expenses, workspace.id
    )

    if skipped_expense_ids:
        skipped_expenses = mark_expenses_as_skipped(Q(), skipped_expense_ids, workspace)
        if skipped_expenses:
            try:
                post_accounting_export_summary(workspace_id=workspace.id, expense_ids=[expense.id for expense in skipped_expenses])
            except Exception:
                logger.error('Error posting accounting export summary for workspace_id: %s', workspace.id)

    if task_log:
        task_log.status = 'COMPLETE'
        task_log.updated_at = datetime.now()
        task_log.save(update_fields=['status', 'updated_at'])


def create_expense_groups(workspace_id: int, fund_source: List[str], task_log: TaskLog | None, imported_from: ExpenseImportSourceEnum):
    try:
        with transaction.atomic():

            expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
            workspace = Workspace.objects.get(pk=workspace_id)
            ccc_last_synced_at = workspace.ccc_last_synced_at if imported_from != ExpenseImportSourceEnum.CONFIGURATION_UPDATE else None
            last_synced_at = workspace.last_synced_at if imported_from != ExpenseImportSourceEnum.CONFIGURATION_UPDATE else None
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
                        filter_credit_expenses=False,
                        last_paid_at=last_paid_at,
                    )
                )

            if workspace.ccc_last_synced_at or len(expenses) != reimbursable_expense_count:
                workspace.ccc_last_synced_at = datetime.now()

            if imported_from != ExpenseImportSourceEnum.CONFIGURATION_UPDATE:
                workspace.save()

            system_comments = []
            group_expenses_and_save(expenses, task_log, workspace, imported_from=imported_from, filter_credit_expenses=filter_credit_expenses, system_comments=system_comments)

            if system_comments:
                SystemComment.bulk_create_comments(system_comments)

    except FyleCredential.DoesNotExist:
        logger.info("Fyle credentials not found %s", workspace_id)
        update_task_log_post_import(
            task_log,
            'FAILED',
            "Fyle credentials do not exist in workspace"
        )

    except FyleInvalidTokenError:
        logger.info("Invalid Token for Fyle")
        update_task_log_post_import(
            task_log,
            'FAILED',
            "Invalid Fyle credentials"
        )

    except (RetryException, InternalServerError) as e:
        error_msg = f"Fyle {e.__class__.__name__} occurred"
        logger.info("%s in workspace_id: %s", error_msg, workspace_id)
        update_task_log_post_import(
            task_log,
            'FATAL' if isinstance(e, RetryException) else 'FAILED',
            error_msg
        )

    except Exception:
        error = traceback.format_exc()
        logger.exception(
            "Something unexpected happened workspace_id: %s",
            workspace_id
        )
        update_task_log_post_import(task_log, 'FATAL', error=error)


def sync_dimensions(workspace_id: int, is_export: bool = False):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)
    platform.import_fyle_dimensions(is_export=is_export)
    if is_export:
        categories_count = platform.categories.get_count()

        categories_expense_attribute_count = ExpenseAttribute.objects.filter(
            attribute_type="CATEGORY", workspace_id=workspace_id, active=True
        ).count()

        if categories_count != categories_expense_attribute_count:
            platform.categories.sync()

        projects_count = platform.projects.get_count()

        projects_expense_attribute_count = ExpenseAttribute.objects.filter(
            attribute_type="PROJECT", workspace_id=workspace_id, active=True
        ).count()

        if projects_count != projects_expense_attribute_count:
            platform.projects.sync()


def import_and_export_expenses(report_id: str, org_id: str, is_state_change_event: bool, report_state: str = None, imported_from: ExpenseImportSourceEnum = None) -> None:
    """
    Import and export expenses
    :param report_id: report id
    :param org_id: org id
    :return: None
    """
    task_log = None
    workspace = Workspace.objects.get(fyle_org_id=org_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace.id)

    import_states = get_expense_import_states(expense_group_settings)

    # Don't call API if report state is not in import states, for example customer configured to import only PAID reports but webhook is triggered for APPROVED report (this is only for is_state_change_event webhook calls)
    if is_state_change_event and report_state and report_state not in import_states:
        return

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace.id)
    task_log = None

    try:
        with transaction.atomic():
            fund_source = get_fund_source(workspace.id)

            if imported_from == ExpenseImportSourceEnum.DIRECT_EXPORT:
                source_account_type = ['PERSONAL_CASH_ACCOUNT', 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT']
            else:
                source_account_type = get_source_account_type(fund_source)

            filter_credit_expenses = get_filter_credit_expenses(expense_group_settings)

            task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace.id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

            expenses_count = Expense.objects.filter(workspace_id=workspace.id, report_id=report_id).count()
            platform = PlatformConnector(fyle_credentials)

            try:
                if expenses_count > 0 and report_state in ('APPROVED', 'ADMIN_APPROVED'):
                    logger.info("Handling expense fund source change for workspace_id: %s, report_id: %s", workspace.id, report_id)
                    handle_expense_fund_source_change(workspace.id, report_id, platform)
            except Exception as e:
                logger.exception("Error handling expense fund source change for workspace_id: %s, report_id: %s | ERROR: %s", workspace.id, report_id, e)
            expenses = platform.expenses.get(
                source_account_type,
                filter_credit_expenses=False,
                report_id=report_id,
                import_states=import_states if is_state_change_event else None
            )

            if is_state_change_event:
                expenses = filter_expenses_based_on_state(expenses, expense_group_settings)

            system_comments = []
            group_expenses_and_save(expenses, task_log, workspace, imported_from=imported_from, filter_credit_expenses=filter_credit_expenses, system_comments=system_comments)

            if system_comments:
                SystemComment.bulk_create_comments(system_comments)

        # Export only selected expense groups
        expense_ids = Expense.objects.filter(report_id=report_id, org_id=org_id).values_list('id', flat=True)
        expense_groups = ExpenseGroup.objects.filter(expenses__id__in=[expense_ids], workspace_id=workspace.id, exported_at__isnull=True).distinct('id').values('id')
        expense_group_ids = [expense_group['id'] for expense_group in expense_groups]

        if len(expense_group_ids):
            if is_state_change_event:
                # Trigger export immediately for customers who have enabled real time export
                is_real_time_export_enabled = WorkspaceSchedule.objects.filter(workspace_id=workspace.id, is_real_time_export_enabled=True).exists()

                # Don't allow real time export if it's not supported for the branded app / setting not enabled
                if not is_real_time_export_enabled or not feature_configuration.feature.real_time_export_1hr_orgs:
                    return

            logger.info('Exporting expenses for workspace %s with expense group ids %s, triggered by %s', workspace.id, expense_group_ids, imported_from)
            export_to_qbo(
                workspace_id=workspace.id,
                expense_group_ids=expense_group_ids,
                is_direct_export=True if not is_state_change_event else False,
                triggered_by=imported_from,
                run_in_rabbitmq_worker=True
            )

    except WorkspaceGeneralSettings.DoesNotExist:
        logger.info('Workspace general settings not found %s', workspace.id)
        if not task_log:
            task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace.id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

        task_log.detail = {'message': 'Workspace general settings do not exist in workspace'}
        task_log.status = 'FAILED'
        task_log.re_attempt_export = False
        task_log.save()

    except Exception:
        if not task_log:
            task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace.id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

        handle_import_exception(task_log)


def handle_expense_fund_source_change(workspace_id: int, report_id: str, platform: PlatformConnector) -> None:
    """
    Handle expense fund source change
    :param workspace_id: Workspace id
    :param report_id: Report id
    :param platform: Platform connector
    :return: None
    """
    expenses = platform.expenses.get(
        source_account_type=['PERSONAL_CASH_ACCOUNT', 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'],
        report_id=report_id,
        filter_credit_expenses=False
    )

    expenses_to_update: List[Dict] = []
    expense_ids_changed: List[int] = []
    expenses_in_db = Expense.objects.filter(workspace_id=workspace_id, report_id=report_id).values_list('expense_id', 'fund_source', 'id')
    expense_id_fund_source_map = {
        expense[0]: {
            'fund_source': expense[1],
            'id': expense[2]
        }
        for expense in expenses_in_db
    }

    affected_fund_source_expense_ids: dict[str, List[int]] = {
        'PERSONAL': [],
        'CCC': []
    }

    for expense in expenses:
        if expense['id'] in expense_id_fund_source_map:
            new_expense_fund_source = EXPENSE_SOURCE_ACCOUNT_MAP[expense['source_account_type']]
            old_expense_fund_source = expense_id_fund_source_map[expense['id']]['fund_source']
            if new_expense_fund_source != old_expense_fund_source:
                logger.info("Expense Fund Source changed for expense %s from %s to %s", expense['id'], old_expense_fund_source, new_expense_fund_source)
                expenses_to_update.append(expense)
                expense_ids_changed.append(expense_id_fund_source_map[expense['id']]['id'])
                affected_fund_source_expense_ids[old_expense_fund_source].append(expense_id_fund_source_map[expense['id']]['id'])

    if expenses_to_update:
        logger.info("Updating Fund Source Change for expenses with report_id %s in workspace %s | COUNT %s", report_id, workspace_id, len(expenses_to_update))
        Expense.create_expense_objects(expenses=expenses_to_update, workspace_id=workspace_id, skip_update=False)

        system_comments = []
        handle_fund_source_changes_for_expense_ids(workspace_id=workspace_id, changed_expense_ids=expense_ids_changed, report_id=report_id, affected_fund_source_expense_ids=affected_fund_source_expense_ids, system_comments=system_comments)

        for expense in expenses_to_update:
            expense_db_id = expense_id_fund_source_map[expense['id']]['id']
            old_fund_source = expense_id_fund_source_map[expense['id']]['fund_source']
            new_fund_source = EXPENSE_SOURCE_ACCOUNT_MAP[expense['source_account_type']]

            add_system_comment(
                system_comments=system_comments,
                source=SystemCommentSourceEnum.HANDLE_FUND_SOURCE_CHANGE,
                intent=SystemCommentIntentEnum.UPDATE_EXPENSE_FUND_SOURCE,
                entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                workspace_id=workspace_id,
                entity_id=expense_db_id,
                reason=SystemCommentReasonEnum.FUND_SOURCE_CHANGED.value.format(old=old_fund_source, new=new_fund_source),
                info={'old_fund_source': old_fund_source, 'new_fund_source': new_fund_source}
            )

        if system_comments:
            SystemComment.bulk_create_comments(system_comments)


def handle_fund_source_changes_for_expense_ids(workspace_id: int, changed_expense_ids: List[int], report_id: str, affected_fund_source_expense_ids: dict[str, List[int]], task_name: str = None, system_comments: list = None) -> None:
    """
    Main entry point for handling fund_source changes for expense ids
    :param workspace_id: workspace id
    :param changed_expense_ids: List of expense IDs whose fund_source changed
    :param report_id: Report id
    :param affected_fund_source_expense_ids: Dict of affected fund sources and their expense ids
    :param task_name: Name of the task to clean up
    :param system_comments: Optional list to collect system comment data
    :return: None
    """

    filter_for_affected_expense_groups = construct_filter_for_affected_expense_groups(workspace_id=workspace_id, report_id=report_id, changed_expense_ids=changed_expense_ids, affected_fund_source_expense_ids=affected_fund_source_expense_ids)

    with transaction.atomic():
        affected_groups = ExpenseGroup.objects.filter(
            filter_for_affected_expense_groups,
            workspace_id=workspace_id,
            exported_at__isnull=True
        ).annotate(
            expense_count=Count('expenses')
        ).distinct()

        if not affected_groups:
            logger.info("No expense groups found for changed expenses: %s in workspace %s", changed_expense_ids, workspace_id)
            return

        affected_expense_ids = list(affected_groups.values_list('expenses__id', flat=True))

        are_all_expense_groups_exported = True

        for group in affected_groups:
            logger.info("Processing fund source change for expense group %s with %s expenses in workspace %s", group.id, group.expense_count, workspace_id)
            is_expense_group_processed = process_expense_group_for_fund_source_update(
                expense_group=group,
                changed_expense_ids=changed_expense_ids,
                workspace_id=workspace_id,
                report_id=report_id,
                affected_fund_source_expense_ids=affected_fund_source_expense_ids,
                system_comments=system_comments
            )

            if not is_expense_group_processed:
                are_all_expense_groups_exported = False

        if are_all_expense_groups_exported:
            logger.info("All expense groups are exported or are not initiated, proceeding with recreation of expense groups for changed expense ids %s in workspace %s", changed_expense_ids, workspace_id)
            recreate_expense_groups(workspace_id=workspace_id, expense_ids=affected_expense_ids, system_comments=system_comments)
            cleanup_scheduled_task(task_name=task_name, workspace_id=workspace_id)
        else:
            logger.info("Not all expense groups are exported, skipping recreation of expense groups for changed expense ids %s in workspace %s", changed_expense_ids, workspace_id)
            return


def process_expense_group_for_fund_source_update(expense_group: ExpenseGroup, changed_expense_ids: List[int], workspace_id: int, report_id: str, affected_fund_source_expense_ids: dict[str, List[int]], system_comments: list = None) -> bool:
    """
    Process individual expense group based on task log state
    :param expense_group: Expense group
    :param changed_expense_ids: List of expense IDs whose fund_source changed
    :param workspace_id: Workspace id
    :param report_id: Report id
    :param affected_fund_source_expense_ids: Dict of affected fund sources and their expense ids
    :param system_comments: Optional list to collect system comment data
    :return: bool indicating if group can be processed now
    """

    # this is to prevent update the task logs from different transactions
    task_log = TaskLog.objects.select_for_update().filter(
        ~Q(type__in=['CREATING_REIMBURSEMENT', 'CREATING_AP_PAYMENT']),
        expense_group_id=expense_group.id,
        workspace_id=expense_group.workspace_id
    ).order_by('-created_at').first()

    if task_log:
        logger.info("Task log for expense group %s in %s state for workspace %s", expense_group.id, task_log.status, expense_group.workspace_id)
        if task_log.status in ['ENQUEUED', 'IN_PROGRESS']:
            schedule_task_for_expense_group_fund_source_change(changed_expense_ids=changed_expense_ids, workspace_id=workspace_id, report_id=report_id, affected_fund_source_expense_ids=affected_fund_source_expense_ids)
            return False

        elif task_log.status == 'COMPLETE':
            logger.info("Skipping expense group %s - already exported successfully", expense_group.id)
            return False

    logger.info("Proceeding with processing for expense group %s in workspace %s", expense_group.id, expense_group.workspace_id)
    delete_expense_group_and_related_data(expense_group=expense_group, workspace_id=workspace_id, system_comments=system_comments)
    return True


def delete_expense_group_and_related_data(expense_group: ExpenseGroup, workspace_id: int, system_comments: list = None) -> None:
    """
    Delete expense group and all related data safely
    :param expense_group: Expense group
    :param workspace_id: Workspace id
    :param system_comments: Optional list to collect system comment data
    :return: None
    """
    group_id = expense_group.id

    # Delete task logs
    task_logs_deleted = TaskLog.objects.filter(
        ~Q(type__in=['CREATING_REIMBURSEMENT', 'CREATING_AP_PAYMENT']),
        expense_group_id=group_id,
        workspace_id=workspace_id
    ).delete()
    logger.info("Deleted %s task logs for group %s in workspace %s", task_logs_deleted[0], group_id, workspace_id)

    # Delete errors
    errors_deleted = Error.objects.filter(
        expense_group_id=group_id,
        workspace_id=workspace_id
    ).delete()
    logger.info("Deleted %s error logs for group %s in workspace %s", errors_deleted[0], group_id, workspace_id)

    # mapping_error_expense_group_ids in Error model
    error_objects = Error.objects.filter(
        mapping_error_expense_group_ids__contains=[group_id],
        workspace_id=workspace_id
    )
    for error in error_objects:
        logger.info("Removing expensegroup %s from mapping_error_expense_group_ids for error %s in workspace %s", group_id, error.id, workspace_id)
        error.mapping_error_expense_group_ids.remove(group_id)
        if error.mapping_error_expense_group_ids:
            error.save(update_fields=['mapping_error_expense_group_ids'])
        else:
            error.delete()

    # Delete the expense group (this will also delete expense_group_expenses relationships)
    expense_group.delete()
    logger.info("Deleted expense group %s in workspace %s", group_id, workspace_id)

    add_system_comment(
        system_comments=system_comments,
        source=SystemCommentSourceEnum.DELETE_EXPENSE_GROUP_AND_RELATED_DATA,
        intent=SystemCommentIntentEnum.DELETE_EXPENSE_GROUP,
        entity_type=SystemCommentEntityTypeEnum.EXPENSE_GROUP,
        workspace_id=workspace_id,
        entity_id=group_id,
        reason=SystemCommentReasonEnum.EXPENSE_GROUP_AND_RELATED_DATA_DELETED
    )


def recreate_expense_groups(workspace_id: int, expense_ids: List[int], system_comments: list = None) -> None:
    """
    Recreate expense groups using standard grouping logic
    :param workspace_id: Workspace id
    :param expense_ids: List of expense IDs
    :param system_comments: Optional list to collect system comment data
    :return: None
    """
    logger.info("Recreating expense groups for %s expenses in workspace %s", len(expense_ids), workspace_id)

    expenses = Expense.objects.filter(
        id__in=expense_ids,
        expensegroup__exported_at__isnull=True,
        workspace_id=workspace_id
    )

    if not expenses:
        logger.warning("No expenses found for recreation: %s in workspace %s", expense_ids, workspace_id)
        return

    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    # Delete reimbursable expenses if reimbursable expense settings is not configured
    if not configuration.reimbursable_expenses_object:
        reimbursable_expense_ids = [e.id for e in expenses if e.fund_source == 'PERSONAL']

        if reimbursable_expense_ids:
            expenses = [e for e in expenses if e.id not in reimbursable_expense_ids]
            delete_expenses_in_db(expense_ids=reimbursable_expense_ids, workspace_id=workspace_id, system_comments=system_comments)

    # Delete corporate credit card expenses if corporate credit card expense settings is not configured
    if not configuration.corporate_credit_card_expenses_object:
        ccc_expense_ids = [e.id for e in expenses if e.fund_source == 'CCC']

        if ccc_expense_ids:
            expenses = [e for e in expenses if e.id not in ccc_expense_ids]
            delete_expenses_in_db(expense_ids=ccc_expense_ids, workspace_id=workspace_id, system_comments=system_comments)

    expense_objects = expenses
    filters = ExpenseFilter.objects.filter(workspace_id=workspace_id).order_by('rank')
    skipped_expense_ids = []

    if filters:
        filtered_expense_query = construct_expense_filter_query(filters)
        expense_ids_for_filter = [e.id for e in expenses]
        skip_expenses_and_post_accounting_export_summary(expense_ids=expense_ids_for_filter, workspace=configuration.workspace, q_filters=filtered_expense_query)

        expense_objects = Expense.objects.filter(
            id__in=[e.id for e in expenses],
            is_skipped=False,
            workspace_id=workspace_id
        )

    expense_group_objects, skipped_expense_ids = ExpenseGroup.create_expense_groups_by_report_id_fund_source(
        expense_objects, workspace_id
    )

    if skipped_expense_ids:
        workspace = configuration.workspace
        skip_expenses_and_post_accounting_export_summary(expense_ids=skipped_expense_ids, workspace=workspace)
        logger.info("Some expenses were skipped during expense group re-creation: %s in workspace %s", skipped_expense_ids, workspace_id)

    logger.info("Successfully recreated expense groups for %s expenses in workspace %s", len(expense_ids), workspace_id)

    add_system_comment(
        system_comments=system_comments,
        source=SystemCommentSourceEnum.RECREATE_EXPENSE_GROUPS,
        intent=SystemCommentIntentEnum.RECREATE_EXPENSE_GROUPS,
        entity_type=SystemCommentEntityTypeEnum.EXPENSE_GROUP,
        workspace_id=workspace_id,
        reason=SystemCommentReasonEnum.EXPENSE_GROUPS_RECREATED,
        info={'expense_count': len(expense_ids), 'expense_ids': expense_ids, 'skipped_expense_ids': skipped_expense_ids}
    )


def schedule_task_for_expense_group_fund_source_change(changed_expense_ids: List[int], workspace_id: int, report_id: str, affected_fund_source_expense_ids: dict[str, List[int]]) -> None:
    """
    Schedule expense group for later processing when task logs are no longer active
    :param changed_expense_ids: List of expense IDs whose fund_source changed
    :param workspace_id: Workspace id
    :param report_id: Report id
    :param affected_fund_source_expense_ids: Dict of affected fund sources and their expense ids
    :return: None
    """
    logger.info("Scheduling for later processing for changed expense ids %s in workspace %s", changed_expense_ids, workspace_id)

    # generate some random string to avoid duplicate tasks
    hashed_name = hashlib.md5(str(changed_expense_ids).encode('utf-8')).hexdigest()[0:6]

    # Check if there's already a scheduled task for this expense group to avoid duplicates
    task_name = f'fund_source_change_retry_{hashed_name}_{workspace_id}'
    existing_schedule = Schedule.objects.filter(
        func='apps.fyle.tasks.handle_fund_source_changes_for_expense_ids',
        name=task_name
    ).first()

    if existing_schedule:
        logger.info("Task already scheduled for changed expense ids %s in workspace %s", changed_expense_ids, workspace_id)
        return

    schedule_time = datetime.now() + timedelta(minutes=5)

    schedule(
        'apps.fyle.tasks.handle_fund_source_changes_for_expense_ids',
        workspace_id,
        changed_expense_ids,
        report_id,
        affected_fund_source_expense_ids,
        task_name,
        repeats=10,  # 10 retries
        schedule_type='M',  # Minute
        minutes=5,  # 5 minutes delay
        timeout=300,  # 5 minutes timeout
        next_run=schedule_time,
        name=task_name
    )

    logger.info("Scheduled delayed processing for changed expense ids %s in workspace %s with name %s", changed_expense_ids, workspace_id, task_name)


def cleanup_scheduled_task(task_name: str, workspace_id: int) -> None:
    """
    Clean up scheduled task
    :param task_name: Name of the task to clean up
    :param workspace_id: Workspace id
    :return: None
    """
    logger.info("Cleaning up scheduled task %s in workspace %s", task_name, workspace_id)

    schedule_obj = Schedule.objects.filter(name=task_name, func='apps.fyle.tasks.handle_fund_source_changes_for_expense_ids').first()
    if schedule_obj:
        schedule_obj.delete()
        logger.info("Cleaned up scheduled task: %s", task_name)
    else:
        logger.info("No scheduled task found to clean up: %s", task_name)


def delete_expenses_in_db(expense_ids: List[int], workspace_id: int, system_comments: list = None) -> None:
    """
    Delete expenses in database
    :param expense_ids: List of expense IDs
    :param workspace_id: Workspace id
    :param system_comments: Optional list to collect system comment data
    :return: None
    """
    deleted_count = Expense.objects.filter(id__in=expense_ids, workspace_id=workspace_id).delete()[0]
    logger.info("Deleted %s expenses in workspace %s", deleted_count, workspace_id)

    add_system_comment(
        system_comments=system_comments,
        source=SystemCommentSourceEnum.DELETE_EXPENSES,
        intent=SystemCommentIntentEnum.DELETE_EXPENSES,
        entity_type=SystemCommentEntityTypeEnum.EXPENSE,
        workspace_id=workspace_id,
        reason=SystemCommentReasonEnum.EXPENSES_DELETED_NO_EXPORT_SETTING,
        info={'expense_ids': expense_ids}
    )


def update_non_exported_expenses(data: Dict) -> None:
    """
    To update expenses not in COMPLETE, IN_PROGRESS state
    """
    try:
        expense_state = None
        org_id = data['org_id']
        expense_id = data['id']
        workspace = Workspace.objects.get(fyle_org_id=org_id)
        expense = Expense.objects.filter(workspace_id=workspace.id, expense_id=expense_id).first()

        if expense:
            if 'state' in expense.accounting_export_summary:
                expense_state = expense.accounting_export_summary['state']
            else:
                expense_state = 'NOT_EXPORTED'

            if expense_state and expense_state not in ['COMPLETE', 'IN_PROGRESS']:
                system_comments = []
                fyle_credentials = FyleCredential.objects.get(workspace_id=expense.workspace_id)
                platform = PlatformConnector(fyle_credentials)

                expense_obj = []
                expense_obj.append(data)
                expense_objects = platform.expenses.construct_expense_object(expense_obj, expense.workspace_id)

                old_fund_source = expense.fund_source
                old_category = expense.category if (expense.category == expense.sub_category or expense.sub_category == None) else '{0} / {1}'.format(expense.category, expense.sub_category)
                new_fund_source = EXPENSE_SOURCE_ACCOUNT_MAP[expense_objects[0]['source_account_type']]
                new_category = expense_objects[0]['category'] if (expense_objects[0]['category'] == expense_objects[0]['sub_category'] or expense_objects[0]['sub_category'] == None) else '{0} / {1}'.format(expense_objects[0]['category'], expense_objects[0]['sub_category'])

                Expense.create_expense_objects(
                    expense_objects, expense.workspace_id, skip_update=True
                )

                if old_fund_source != new_fund_source:
                    logger.info("Fund source changed for expense %s from %s to %s in workspace %s", expense.id, old_fund_source, new_fund_source, expense.workspace_id)
                    handle_fund_source_changes_for_expense_ids(
                        workspace_id=expense.workspace_id,
                        changed_expense_ids=[expense.id],
                        report_id=expense.report_id,
                        affected_fund_source_expense_ids={old_fund_source: [expense.id]},
                        system_comments=system_comments
                    )

                    add_system_comment(
                        system_comments=system_comments,
                        source=SystemCommentSourceEnum.HANDLE_FUND_SOURCE_CHANGE,
                        intent=SystemCommentIntentEnum.UPDATE_EXPENSE_FUND_SOURCE,
                        workspace_id=expense.workspace_id,
                        entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                        entity_id=expense.id,
                        reason=SystemCommentReasonEnum.FUND_SOURCE_CHANGED.value.format(old=old_fund_source, new=new_fund_source),
                        info={'old_fund_source': old_fund_source, 'new_fund_source': new_fund_source}
                    )

                if old_category != new_category:
                    logger.info("Category changed for expense %s from %s to %s in workspace %s", expense.id, old_category, new_category, expense.workspace_id)
                    handle_category_changes_for_expense(expense=expense, new_category=new_category, system_comments=system_comments)

                if system_comments:
                    SystemComment.bulk_create_comments(system_comments)

    except (FyleInvalidTokenError, FyleExpiredTokenError) as exception:
        logger.info('Fyle token expired, workspace_id: %s %s', expense.workspace_id, str(exception))
    except Exception as exception:
        logger.info('Error while refreshing Fyle dimensions, workspace_id: %s %s', expense.workspace_id, str(exception))


def handle_category_changes_for_expense(expense: Expense, new_category: str, system_comments: list = None) -> None:
    """
    Handle category changes for expense
    :param expense: Expense object
    :param new_category: New category
    :param system_comments: Optional list to collect system comment data
    :return: None
    """
    old_category = expense.category
    with transaction.atomic():
        expense_group = ExpenseGroup.objects.filter(expenses__id=expense.id, workspace_id=expense.workspace_id).first()
        if expense_group:
            error = Error.objects.filter(workspace_id=expense.workspace_id, is_resolved=False, type='CATEGORY_MAPPING', mapping_error_expense_group_ids__contains=[expense_group.id]).first()
            if error:
                logger.info('Removing expense group: %s from errors for workspace_id: %s as a result of category update for expense %s', expense_group.id, expense.workspace_id, expense.id)
                error.mapping_error_expense_group_ids.remove(expense_group.id)
                if error.mapping_error_expense_group_ids:
                    error.updated_at = datetime.now(timezone.utc)
                    error.save(update_fields=['mapping_error_expense_group_ids', 'updated_at'])
                else:
                    error.delete()

            new_category_expense_attribute = ExpenseAttribute.objects.filter(workspace_id=expense.workspace_id, attribute_type='CATEGORY', value=new_category).first()
            if new_category_expense_attribute:
                updated_category_error = Error.objects.filter(workspace_id=expense.workspace_id, is_resolved=False, type='CATEGORY_MAPPING', expense_attribute=new_category_expense_attribute).first()
                if updated_category_error:
                    updated_category_error.mapping_error_expense_group_ids.append(expense_group.id)
                    updated_category_error.updated_at = datetime.now(timezone.utc)
                    updated_category_error.save(update_fields=['mapping_error_expense_group_ids', 'updated_at'])
                else:
                    mapping = Mapping.objects.filter(
                        source_type='CATEGORY',
                        destination_type='ACCOUNT',
                        source=new_category_expense_attribute,
                        workspace_id=expense_group.workspace_id
                    ).first()
                    if not mapping:
                        Error.objects.create(
                            workspace_id=expense.workspace_id,
                            type='CATEGORY_MAPPING',
                            expense_attribute=new_category_expense_attribute,
                            mapping_error_expense_group_ids=[expense_group.id],
                            updated_at=datetime.now(timezone.utc),
                            error_detail=f"{new_category_expense_attribute.display_name} mapping is missing",
                            error_title=new_category_expense_attribute.value
                        )

        add_system_comment(
            system_comments=system_comments,
            source=SystemCommentSourceEnum.HANDLE_EXPENSE_CATEGORY_CHANGE,
            intent=SystemCommentIntentEnum.UPDATE_EXPENSE_CATEGORY,
            entity_type=SystemCommentEntityTypeEnum.EXPENSE,
            workspace_id=expense.workspace_id,
            entity_id=expense.id,
            reason=SystemCommentReasonEnum.CATEGORY_CHANGED.value.format(old=old_category, new=new_category),
            info={'old_category': old_category, 'new_category': new_category}
        )


def handle_expense_report_change(expense_data: Dict, action_type: str) -> None:
    """
    Handle expense report changes (EJECTED_FROM_REPORT, ADDED_TO_REPORT)
    :param expense_data: Expense data from webhook
    :param action_type: Type of action (EJECTED_FROM_REPORT or ADDED_TO_REPORT)
    :return: None
    """
    org_id = expense_data['org_id']
    expense_id = expense_data['id']
    workspace = Workspace.objects.get(fyle_org_id=org_id)
    system_comments = []

    if action_type == 'ADDED_TO_REPORT':
        report_id = expense_data.get('report_id')

        logger.info("Processing ADDED_TO_REPORT for expense %s in workspace %s, report_id: %s", expense_id, workspace.id, report_id)
        _delete_expense_groups_for_report(report_id, workspace, system_comments=system_comments)

        if Expense.objects.filter(report_id=report_id, workspace_id=workspace.id).exists():
            add_system_comment(
                system_comments=system_comments,
                source=SystemCommentSourceEnum.HANDLE_REPORT_CHANGE,
                intent=SystemCommentIntentEnum.UPDATE_EXPENSE_REPORT,
                entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                workspace_id=workspace.id,
                reason=SystemCommentReasonEnum.EXPENSE_ADDED_TO_REPORT,
                info={'report_id': report_id, 'expense_id': expense_id}
            )

        if system_comments:
            SystemComment.bulk_create_comments(system_comments)
            logger.info("Created %s system comments for expense %s in workspace %s", len(system_comments), expense_id, workspace.id)

        return

    elif action_type == 'EJECTED_FROM_REPORT':
        expense = Expense.objects.filter(workspace_id=workspace.id, expense_id=expense_id).first()

        if not expense:
            logger.warning("Expense %s not found in workspace %s for action %s", expense_id, workspace.id, action_type)
            return

        expense_group = ExpenseGroup.objects.filter(
            expenses=expense,
            workspace_id=workspace.id,
            exported_at__isnull=False
        ).first()

        if expense_group:
            logger.info("Skipping %s for expense %s as it's part of exported expense group %s", action_type, expense_id, expense_group.id)
            return

        logger.info("Processing %s for expense %s in workspace %s", action_type, expense_id, workspace.id)
        _handle_expense_ejected_from_report(expense, expense_data, workspace, system_comments=system_comments)

        if system_comments:
            SystemComment.bulk_create_comments(system_comments)
            logger.info("Created %s system comments for expense %s in workspace %s", len(system_comments), expense_id, workspace.id)


def _delete_expense_groups_for_report(report_id: str, workspace: Workspace, system_comments: list = None) -> None:
    """
    Delete all non-exported expense groups for a report
    When expenses are added to a report, the report goes to SUBMITTED state which is not importable.
    This function deletes all expense groups for the report so they can be recreated when the report
    changes to an importable state (APPROVED/PAYMENT_PROCESSING/PAID) via state change webhook.

    :param report_id: Report ID
    :param workspace: Workspace object
    :param system_comments: Optional list to collect system comment data
    :return: None
    """
    logger.info("Deleting expense groups for report %s in workspace %s", report_id, workspace.id)

    expense_ids = Expense.objects.filter(
        workspace_id=workspace.id,
        report_id=report_id
    ).values_list('id', flat=True)

    if not expense_ids:
        logger.info("No expenses found for report %s in workspace %s", report_id, workspace.id)
        return

    expense_groups = ExpenseGroup.objects.filter(
        expenses__id__in=expense_ids,
        workspace_id=workspace.id,
        exported_at__isnull=True
    ).distinct()

    deleted_count = 0
    skipped_count = 0

    for expense_group in expense_groups:
        active_task_logs = TaskLog.objects.filter(
            expense_group_id=expense_group.id,
            workspace_id=workspace.id,
            status__in=['ENQUEUED', 'IN_PROGRESS']
        ).exists()

        if active_task_logs:
            logger.warning("Skipping deletion of expense group %s - active task logs exist", expense_group.id)
            skipped_count += 1
            continue

        logger.info("Deleting expense group %s for report %s", expense_group.id, report_id)

        with transaction.atomic():
            delete_expense_group_and_related_data(expense_group, workspace.id, system_comments=system_comments)

        deleted_count += 1

    logger.info("Completed deletion for report %s in workspace %s - deleted: %s, skipped: %s",
                report_id, workspace.id, deleted_count, skipped_count)


def _handle_expense_ejected_from_report(expense: Expense, expense_data: Dict, workspace: Workspace, system_comments: list = None) -> None:
    """
    Handle expense ejected from report
    :param expense: Expense object
    :param expense_data: Expense data from webhook
    :param workspace: Workspace object
    :param system_comments: Optional list to collect system comment data
    :return: None
    """
    logger.info("Handling expense %s ejected from report in workspace %s", expense.expense_id, workspace.id)

    expense_group = ExpenseGroup.objects.filter(
        expenses=expense,
        workspace_id=workspace.id,
        exported_at__isnull=True
    ).first()

    if not expense_group:
        logger.info("No expense group found for expense %s in workspace %s", expense.expense_id, workspace.id)
        return

    logger.info("Removing expense %s from expense group %s", expense.expense_id, expense_group.id)

    active_task_logs = TaskLog.objects.filter(
        expense_group_id=expense_group.id,
        workspace_id=workspace.id,
        status__in=['ENQUEUED', 'IN_PROGRESS']
    ).exists()

    if active_task_logs:
        logger.warning("Cannot remove expense %s from group %s - active task logs exist", expense.expense_id, expense_group.id)
        return

    with transaction.atomic():
        expense_group.expenses.remove(expense)
        expense_group_deleted = False

        if not expense_group.expenses.exists():
            logger.info("Deleting empty expense group %s after removing expense %s", expense_group.id, expense.expense_id)
            delete_expense_group_and_related_data(expense_group, workspace.id, system_comments=system_comments)
            expense_group_deleted = True
        else:
            logger.info("Expense group %s still has expenses after removing %s", expense_group.id, expense.expense_id)

        add_system_comment(
            system_comments=system_comments,
            source=SystemCommentSourceEnum.HANDLE_REPORT_CHANGE,
            intent=SystemCommentIntentEnum.UPDATE_EXPENSE_REPORT,
            entity_type=SystemCommentEntityTypeEnum.EXPENSE,
            workspace_id=workspace.id,
            entity_id=expense.id,
            reason=SystemCommentReasonEnum.EXPENSE_EJECTED_FROM_REPORT,
            info={'report_id': expense.report_id, 'is_expense_group_deleted': expense_group_deleted}
        )


def re_run_skip_export_rule(workspace: Workspace) -> None:
    """
    Skip expenses before export
    :param workspace_id: Workspace id
    :return: None
    """
    expense_filters = ExpenseFilter.objects.filter(workspace_id=workspace.id).order_by('rank')
    if expense_filters:
        filtered_expense_query = construct_expense_filter_query(expense_filters)
        # Get all expenses matching the filter query, excluding those in COMPLETE state
        expenses = Expense.objects.filter(
            filtered_expense_query, workspace_id=workspace.id, is_skipped=False
        ).filter(
            Q(accounting_export_summary={}) | ~Q(accounting_export_summary__state="COMPLETE")
        )
        expense_ids = list(expenses.values_list('id', flat=True))
        skipped_expenses = mark_expenses_as_skipped(
            filtered_expense_query,
            expense_ids,
            workspace
        )
        if skipped_expenses:
            system_comments = []
            for expense in skipped_expenses:
                add_system_comment(
                    system_comments=system_comments,
                    source=SystemCommentSourceEnum.GROUP_EXPENSES_AND_SAVE,
                    intent=SystemCommentIntentEnum.SKIP_EXPENSE,
                    entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                    workspace_id=workspace.id,
                    entity_id=expense.id,
                    reason=SystemCommentReasonEnum.EXPENSE_SKIPPED_AFTER_IMPORT
                )

            if system_comments:
                SystemComment.bulk_create_comments(system_comments)

            expense_groups = ExpenseGroup.objects.filter(exported_at__isnull=True, workspace_id=workspace.id, expenses__in=skipped_expenses)
            deleted_failed_expense_groups_count = 0
            deleted_total_expense_groups_count = 0
            for expense_group in expense_groups:
                task_log = TaskLog.objects.filter(
                    workspace_id=workspace.id,
                    expense_group_id=expense_group.id
                ).first()
                if task_log:
                    if task_log.status != 'COMPLETE':
                        deleted_failed_expense_groups_count += 1
                    logger.info('Deleting task log for expense group %s before export', expense_group.id)
                    task_log.delete()

                error = Error.objects.filter(
                    workspace_id=workspace.id,
                    expense_group_id=expense_group.id
                ).first()
                if error:
                    logger.info('Deleting QBO error for expense group %s before export', expense_group.id)
                    error.delete()

                expense_group.expenses.remove(*skipped_expenses)
                if not expense_group.expenses.exists():
                    logger.info('Deleting empty expense group %s before export', expense_group.id)
                    expense_group.delete()
                    deleted_total_expense_groups_count += 1

            last_export_detail = LastExportDetail.objects.filter(workspace_id=workspace.id).first()
            if last_export_detail:
                last_export_detail.failed_expense_groups_count = max(
                    0,
                    (last_export_detail.failed_expense_groups_count or 0) - deleted_failed_expense_groups_count
                )
                last_export_detail.total_expense_groups_count = max(
                    0,
                    (last_export_detail.total_expense_groups_count or 0) - deleted_total_expense_groups_count
                )
                last_export_detail.save()
            try:
                post_accounting_export_summary(workspace_id=workspace.id, expense_ids=[expense.id for expense in skipped_expenses])
            except Exception:
                logger.error('Error posting accounting export summary for workspace_id: %s', workspace.id)


def get_grouping_types(workspace_id: int) -> dict[str, str]:
    """
    Get grouping types for a workspace
    :param workspace_id: Workspace id
    :return: Dict of grouping types
    """
    grouping_types = {}

    expense_group_settings = ExpenseGroupSettings.objects.filter(workspace_id=workspace_id).first()

    if expense_group_settings:
        reimbursable_grouping_type = 'report' if 'report_id' in expense_group_settings.reimbursable_expense_group_fields else 'expense'
        ccc_grouping_type = 'report' if 'report_id' in expense_group_settings.corporate_credit_card_expense_group_fields else 'expense'

        grouping_types = {
            'PERSONAL': reimbursable_grouping_type,
            'CCC': ccc_grouping_type
        }

    return grouping_types


def construct_filter_for_affected_expense_groups(workspace_id: int, report_id: str, changed_expense_ids: List[int], affected_fund_source_expense_ids: dict[str, List[int]]) -> Q:
    """
    Construct filter for affected expense groups
    :param workspace_id: Workspace id
    :param report_id: Report id
    :param changed_expense_ids: List of changed expense ids
    :param affected_fund_source_expense_ids: Dict of affected fund source and their expense ids
    :return: Filter for affected expense groups
    """
    grouping_types = get_grouping_types(workspace_id=workspace_id)
    filter_for_affected_expense_groups = Q()

    if grouping_types.get('PERSONAL') == 'report' and grouping_types.get('CCC') == 'report':
        filter_for_affected_expense_groups = Q(
            expenses__report_id=report_id
        )
    elif grouping_types.get('PERSONAL') == 'expense' and grouping_types.get('CCC') == 'expense':
        filter_for_affected_expense_groups = Q(
            expenses__id__in=changed_expense_ids
        )

    for fund_source, expense_ids in affected_fund_source_expense_ids.items():
        if fund_source == 'PERSONAL':
            if grouping_types.get('PERSONAL') == 'report' and grouping_types.get('CCC') == 'expense':
                filter_for_affected_expense_groups |= Q(expenses__report_id=report_id, fund_source='PERSONAL')
                filter_for_affected_expense_groups |= Q(expenses__id__in=expense_ids)
            elif grouping_types.get('PERSONAL') == 'expense' and grouping_types.get('CCC') == 'report':
                filter_for_affected_expense_groups |= Q(expenses__report_id=report_id, fund_source='CCC')
                filter_for_affected_expense_groups |= Q(expenses__id__in=expense_ids)
        else:
            if grouping_types.get('PERSONAL') == 'report' and grouping_types.get('CCC') == 'expense':
                filter_for_affected_expense_groups |= Q(expenses__report_id=report_id, fund_source='CCC')
                filter_for_affected_expense_groups |= Q(expenses__id__in=expense_ids)
            elif grouping_types.get('PERSONAL') == 'expense' and grouping_types.get('CCC') == 'report':
                filter_for_affected_expense_groups |= Q(expenses__report_id=report_id, fund_source='PERSONAL')
                filter_for_affected_expense_groups |= Q(expenses__id__in=expense_ids)

    return filter_for_affected_expense_groups


def handle_org_setting_updated(workspace_id: int, org_settings: dict) -> None:
    """
    Update regional date setting on org setting updated
    :param workspace_id: Workspace id
    :param org_settings: Org settings
    :return: None
    """
    logger.info("Handling org settings update for workspace %s", workspace_id)

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.org_settings = {
        'regional_settings': org_settings.get('regional_settings', {})
    }
    workspace.save(update_fields=['org_settings', 'updated_at'])
    logger.info("Updated org settings for workspace %s", workspace.id)
