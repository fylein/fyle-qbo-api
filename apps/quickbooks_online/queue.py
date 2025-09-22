import logging
from datetime import datetime, timedelta
from typing import List

from django.db.models import Q
from django_q.models import Schedule
from django_q.tasks import Chain
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_accounting_library.rabbitmq.data_class import Task
from fyle_accounting_library.rabbitmq.helpers import TaskChainRunner

from apps.fyle.actions import post_accounting_export_summary_for_skipped_exports, sync_fyle_dimensions
from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.actions import update_last_export_details
from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import WorkspaceGeneralSettings
from workers.helpers import RoutingKeyEnum, WorkerActionEnum, publish_to_rabbitmq

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def async_run_post_configration_triggers(workspace_general_settings: WorkspaceGeneralSettings):
    payload = {
        'workspace_id': workspace_general_settings.workspace.id,
        'action': WorkerActionEnum.SYNC_ACCOUNTS.value,
        'data': {
            'workspace_id': workspace_general_settings.workspace.id
        }
    }
    publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.IMPORT.value)


def handle_skipped_exports(expense_groups: List[ExpenseGroup], index: int, skip_export_count: int, error: Error = None, expense_group: ExpenseGroup = None, triggered_by: ExpenseImportSourceEnum = None):
    """
    Handle common export scheduling logic for skip tracking, logging, posting skipped export summaries, and last export updates.
    """
    total_count = expense_groups.count()
    last_export = (index + 1) == total_count

    skip_reason = f"{error.repetition_count} errors" if error else "mapping errors"
    logger.info(f"Skipping expense group {expense_group.id} due to {skip_reason}")
    skip_export_count += 1
    if triggered_by == ExpenseImportSourceEnum.DIRECT_EXPORT:
        post_accounting_export_summary_for_skipped_exports(
            expense_group, expense_group.workspace_id, is_mapping_error=False if error else True
        )
    if last_export and skip_export_count == total_count:
        update_last_export_details(expense_group.workspace_id)

    return skip_export_count


def validate_failing_export(is_auto_export: bool, interval_hours: int, error: Error, expense_group: ExpenseGroup):
    """
    Validate failing export
    :param is_auto_export: Is auto export
    :param interval_hours: Interval hours
    :param error: Error
    """
    mapping_error = Error.objects.filter(
        workspace_id=expense_group.workspace_id,
        mapping_error_expense_group_ids__contains=[expense_group.id],
        is_resolved=False
    ).first()
    if mapping_error:
        return True


def schedule_bills_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, interval_hours: int, triggered_by: ExpenseImportSourceEnum, run_in_rabbitmq_worker: bool):
    """
    Schedule bills creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :param is_auto_export: is auto export
    :param fund_source: Fund source
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']), workspace_id=workspace_id, id__in=expense_group_ids, bill__id__isnull=True, exported_at__isnull=True).all()

        errors = Error.objects.filter(workspace_id=workspace_id, is_resolved=False, expense_group_id__in=expense_group_ids).all()

        chain_tasks = []
        skip_export_count = 0

        for index, expense_group in enumerate(expense_groups):
            error = errors.filter(workspace_id=workspace_id, expense_group=expense_group, is_resolved=False).first()
            skip_export = validate_failing_export(is_auto_export, interval_hours, error, expense_group)
            if skip_export:
                skip_export_count = handle_skipped_exports(
                    expense_groups=expense_groups, index=index, skip_export_count=skip_export_count,
                    error=error, expense_group=expense_group, triggered_by=triggered_by
                )
                continue

            task_log, _ = TaskLog.objects.get_or_create(workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'status': 'ENQUEUED', 'type': 'CREATING_BILL', 'triggered_by': triggered_by})
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_BILL'
                task_log.status = 'ENQUEUED'
                if triggered_by and task_log.triggered_by != triggered_by:
                    task_log.triggered_by = triggered_by
                task_log.save()

            chain_tasks.append(Task(
                target='apps.quickbooks_online.tasks.create_bill',
                args=[expense_group.id, task_log.id, (expense_groups.count() == index + 1), is_auto_export]
            ))

        if len(chain_tasks) > 0:
            __create_chain_and_run(workspace_id, chain_tasks, run_in_rabbitmq_worker)


def __create_chain_and_run(workspace_id: int, chain_tasks: List[Task], run_in_rabbitmq_worker: bool) -> None:
    """
    Create chain and run
    :param fyle_credentials: Fyle credentials
    :param in_progress_expenses: List of in progress expenses
    :param workspace_id: workspace id
    :param chain_tasks: List of chain tasks
    :param fund_source: Fund source
    :return: None
    """
    if run_in_rabbitmq_worker:
        # This function checks intervals and triggers sync if needed, syncing dimension for all exports is overkill
        sync_fyle_dimensions(workspace_id)

        task_executor = TaskChainRunner()
        task_executor.run(chain_tasks, workspace_id)
    else:
        chain = Chain()

        chain.append('apps.fyle.tasks.sync_dimensions', workspace_id, True)

        for task in chain_tasks:
            logger.info(f"Executing {task.target} with args {task.args} and kwargs {task.kwargs}")
            chain.append(task.target, *task.args)

        chain.run()


def schedule_cheques_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, interval_hours: int, triggered_by: ExpenseImportSourceEnum, run_in_rabbitmq_worker: bool):
    """
    Schedule cheque creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :param is_auto_export: is auto export
    :param fund_source: Fund source
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']), workspace_id=workspace_id, id__in=expense_group_ids, cheque__id__isnull=True, exported_at__isnull=True).all()

        errors = Error.objects.filter(workspace_id=workspace_id, is_resolved=False, expense_group_id__in=expense_group_ids).all()

        chain_tasks = []
        skip_export_count = 0

        for index, expense_group in enumerate(expense_groups):
            error = errors.filter(workspace_id=workspace_id, expense_group=expense_group, is_resolved=False).first()
            skip_export = validate_failing_export(is_auto_export, interval_hours, error, expense_group)
            if skip_export:
                skip_export_count = handle_skipped_exports(
                    expense_groups=expense_groups, index=index, skip_export_count=skip_export_count,
                    error=error, expense_group=expense_group, triggered_by=triggered_by
                )
                continue

            task_log, _ = TaskLog.objects.get_or_create(workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'status': 'ENQUEUED', 'type': 'CREATING_CHECK', 'triggered_by': triggered_by})
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_CHECK'
                task_log.status = 'ENQUEUED'
                if triggered_by and task_log.triggered_by != triggered_by:
                    task_log.triggered_by = triggered_by
                task_log.save()

            chain_tasks.append(Task(
                target='apps.quickbooks_online.tasks.create_cheque',
                args=[expense_group.id, task_log.id, (expense_groups.count() == index + 1), is_auto_export]
            ))

        if len(chain_tasks) > 0:
            __create_chain_and_run(workspace_id, chain_tasks, run_in_rabbitmq_worker)


def schedule_journal_entry_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, interval_hours: int, triggered_by: ExpenseImportSourceEnum, run_in_rabbitmq_worker: bool):
    """
    Schedule journal_entry creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']), workspace_id=workspace_id, id__in=expense_group_ids, journalentry__id__isnull=True, exported_at__isnull=True
        ).all()

        errors = Error.objects.filter(workspace_id=workspace_id, is_resolved=False, expense_group_id__in=expense_group_ids).all()

        chain_tasks = []
        skip_export_count = 0

        for index, expense_group in enumerate(expense_groups):
            error = errors.filter(workspace_id=workspace_id, expense_group=expense_group, is_resolved=False).first()
            skip_export = validate_failing_export(is_auto_export, interval_hours, error, expense_group)
            if skip_export:
                skip_export_count = handle_skipped_exports(
                    expense_groups=expense_groups, index=index, skip_export_count=skip_export_count,
                    error=error, expense_group=expense_group, triggered_by=triggered_by
                )
                continue

            task_log, _ = TaskLog.objects.get_or_create(workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'status': 'ENQUEUED', 'type': 'CREATING_JOURNAL_ENTRY', 'triggered_by': triggered_by})
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_JOURNAL_ENTRY'
                task_log.status = 'ENQUEUED'
                if triggered_by and task_log.triggered_by != triggered_by:
                    task_log.triggered_by = triggered_by
                task_log.save()

            chain_tasks.append(Task(
                target='apps.quickbooks_online.tasks.create_journal_entry',
                args=[expense_group.id, task_log.id, (expense_groups.count() == index + 1), is_auto_export]
            ))

        if len(chain_tasks) > 0:
            __create_chain_and_run(workspace_id, chain_tasks, run_in_rabbitmq_worker)


def schedule_credit_card_purchase_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, interval_hours: int, triggered_by: ExpenseImportSourceEnum, run_in_rabbitmq_worker: bool):
    """
    Schedule credit card purchase creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :param is_auto_export: is auto export
    :param fund_source: Fund source
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']), workspace_id=workspace_id, id__in=expense_group_ids, creditcardpurchase__id__isnull=True, exported_at__isnull=True
        ).all()

        errors = Error.objects.filter(workspace_id=workspace_id, is_resolved=False, expense_group_id__in=expense_group_ids).all()

        chain_tasks = []
        skip_export_count = 0

        for index, expense_group in enumerate(expense_groups):
            error = errors.filter(workspace_id=workspace_id, expense_group=expense_group, is_resolved=False).first()
            skip_export = validate_failing_export(is_auto_export, interval_hours, error, expense_group)
            if skip_export:
                skip_export_count = handle_skipped_exports(
                    expense_groups=expense_groups, index=index, skip_export_count=skip_export_count,
                    error=error, expense_group=expense_group, triggered_by=triggered_by
                )
                continue

            task_log, _ = TaskLog.objects.get_or_create(workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'status': 'ENQUEUED', 'type': 'CREATING_CREDIT_CARD_PURCHASE', 'triggered_by': triggered_by})
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_CREDIT_CARD_PURCHASE'
                task_log.status = 'ENQUEUED'
                if triggered_by and task_log.triggered_by != triggered_by:
                    task_log.triggered_by = triggered_by
                task_log.save()

            chain_tasks.append(Task(
                target='apps.quickbooks_online.tasks.create_credit_card_purchase',
                args=[expense_group.id, task_log.id, (expense_groups.count() == index + 1), is_auto_export]
            ))

        if len(chain_tasks) > 0:
            __create_chain_and_run(workspace_id, chain_tasks, run_in_rabbitmq_worker)


def schedule_qbo_expense_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, interval_hours: int, triggered_by: ExpenseImportSourceEnum, run_in_rabbitmq_worker: bool):
    """
    Schedule QBO expense creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :param is_auto_export: is auto export
    :param fund_source: Fund source
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']), workspace_id=workspace_id, id__in=expense_group_ids, qboexpense__id__isnull=True, exported_at__isnull=True).all()
        errors = Error.objects.filter(workspace_id=workspace_id, is_resolved=False, expense_group_id__in=expense_group_ids).all()

        chain_tasks = []
        skip_export_count = 0

        for index, expense_group in enumerate(expense_groups):
            error = errors.filter(workspace_id=workspace_id, expense_group=expense_group, is_resolved=False).first()
            skip_export = validate_failing_export(is_auto_export, interval_hours, error, expense_group)
            if skip_export:
                skip_export_count = handle_skipped_exports(
                    expense_groups=expense_groups, index=index, skip_export_count=skip_export_count,
                    error=error, expense_group=expense_group, triggered_by=triggered_by
                )
                continue

            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'status': 'ENQUEUED', 'type': 'CREATING_EXPENSE' if expense_group.fund_source == 'PERSONAL' else 'CREATING_DEBIT_CARD_EXPENSE', 'triggered_by': triggered_by}
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_EXPENSE' if expense_group.fund_source == 'PERSONAL' else 'CREATING_DEBIT_CARD_EXPENSE'
                task_log.status = 'ENQUEUED'
                if triggered_by and task_log.triggered_by != triggered_by:
                    task_log.triggered_by = triggered_by
                task_log.save()

            chain_tasks.append(Task(
                target='apps.quickbooks_online.tasks.create_qbo_expense',
                args=[expense_group.id, task_log.id, (expense_groups.count() == index + 1), is_auto_export]
            ))

        if len(chain_tasks) > 0:
            __create_chain_and_run(workspace_id, chain_tasks, run_in_rabbitmq_worker)


def schedule_qbo_objects_status_sync(sync_qbo_to_fyle_payments, workspace_id):
    if sync_qbo_to_fyle_payments:
        start_datetime = datetime.now()
        schedule, _ = Schedule.objects.update_or_create(func='apps.quickbooks_online.tasks.check_qbo_object_status', args='{}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': 24 * 60, 'next_run': start_datetime})
    else:
        schedule: Schedule = Schedule.objects.filter(func='apps.quickbooks_online.tasks.check_qbo_object_status', args='{}'.format(workspace_id)).first()

        if schedule:
            schedule.delete()


def schedule_reimbursements_sync(sync_qbo_to_fyle_payments, workspace_id):
    if sync_qbo_to_fyle_payments:
        start_datetime = datetime.now() + timedelta(hours=12)
        schedule, _ = Schedule.objects.update_or_create(func='apps.quickbooks_online.tasks.process_reimbursements', args='{}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': 24 * 60, 'next_run': start_datetime})
    else:
        schedule: Schedule = Schedule.objects.filter(func='apps.quickbooks_online.tasks.process_reimbursements', args='{}'.format(workspace_id)).first()

        if schedule:
            schedule.delete()
