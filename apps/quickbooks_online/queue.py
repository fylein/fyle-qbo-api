from datetime import datetime, timedelta
from typing import List

from django.db.models import Q
from django_q.models import Schedule
from django_q.tasks import Chain, async_task

from apps.fyle.models import Expense, ExpenseGroup
from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings


def async_run_post_configration_triggers(workspace_general_settings: WorkspaceGeneralSettings):
    async_task('apps.quickbooks_online.tasks.async_sync_accounts', int(workspace_general_settings.workspace_id), q_options={'cluster': 'import'})


def schedule_bills_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, fund_source: str):
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

        chain_tasks = []
        in_progress_expenses = []

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'status': 'ENQUEUED', 'type': 'CREATING_BILL'})
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_BILL'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain_tasks.append({
                'target': 'apps.quickbooks_online.tasks.create_bill',
                'expense_group': expense_group,
                'task_log_id': task_log.id,
                'last_export': last_export
            })

            # Don't include expenses with previous export state as ERROR and it's an auto import/export run
            if not (is_auto_export and expense_group.expenses.first().previous_export_state == 'ERROR'):
                in_progress_expenses.extend(expense_group.expenses.all())

        if len(chain_tasks) > 0:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            __create_chain_and_run(fyle_credentials, in_progress_expenses, workspace_id, chain_tasks, fund_source)


def __create_chain_and_run(fyle_credentials: FyleCredential, in_progress_expenses: List[Expense],
        workspace_id: int, chain_tasks: List[dict], fund_source: str) -> None:
    """
    Create chain and run
    :param fyle_credentials: Fyle credentials
    :param in_progress_expenses: List of in progress expenses
    :param workspace_id: workspace id
    :param chain_tasks: List of chain tasks
    :param fund_source: Fund source
    :return: None
    """
    chain = Chain()

    chain.append('apps.quickbooks_online.tasks.update_expense_and_post_summary', in_progress_expenses, workspace_id, fund_source)
    chain.append('apps.fyle.tasks.sync_dimensions', fyle_credentials)

    for task in chain_tasks:
        chain.append(task['target'], task['expense_group'], task['task_log_id'], task['last_export'])

    chain.append('apps.fyle.tasks.post_accounting_export_summary', fyle_credentials.workspace.fyle_org_id, workspace_id, fund_source)
    chain.run()


def schedule_cheques_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, fund_source: str):
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

        chain_tasks = []
        in_progress_expenses = []

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'status': 'ENQUEUED', 'type': 'CREATING_CHECK'})
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_CHECK'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain_tasks.append({
                'target': 'apps.quickbooks_online.tasks.create_cheque',
                'expense_group': expense_group,
                'task_log_id': task_log.id,
                'last_export': last_export
            })

            # Don't include expenses with previous export state as ERROR and it's an auto import/export run
            if not (is_auto_export and expense_group.expenses.first().previous_export_state == 'ERROR'):
                in_progress_expenses.extend(expense_group.expenses.all())

        if len(chain_tasks) > 0:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            __create_chain_and_run(fyle_credentials, in_progress_expenses, workspace_id, chain_tasks, fund_source)


def schedule_journal_entry_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, fund_source: str):
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

        chain_tasks = []
        in_progress_expenses = []

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'status': 'ENQUEUED', 'type': 'CREATING_JOURNAL_ENTRY'})
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_JOURNAL_ENTRY'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain_tasks.append({
                'target': 'apps.quickbooks_online.tasks.create_journal_entry',
                'expense_group': expense_group,
                'task_log_id': task_log.id,
                'last_export': last_export
            })
            # Don't include expenses with previous export state as ERROR and it's an auto import/export run
            if not (is_auto_export and expense_group.expenses.first().previous_export_state == 'ERROR'):
                in_progress_expenses.extend(expense_group.expenses.all())

        if len(chain_tasks) > 0:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            __create_chain_and_run(fyle_credentials, in_progress_expenses, workspace_id, chain_tasks, fund_source)


def schedule_credit_card_purchase_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, fund_source: str):
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

        chain_tasks = []
        in_progress_expenses = []

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'status': 'ENQUEUED', 'type': 'CREATING_CREDIT_CARD_PURCHASE'})
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_CREDIT_CARD_PURCHASE'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain_tasks.append({
                'target': 'apps.quickbooks_online.tasks.create_credit_card_purchase',
                'expense_group': expense_group,
                'task_log_id': task_log.id,
                'last_export': last_export
            })

            # Don't include expenses with previous export state as ERROR and it's an auto import/export run
            if not (is_auto_export and expense_group.expenses.first().previous_export_state == 'ERROR'):
                in_progress_expenses.extend(expense_group.expenses.all())

        if len(chain_tasks) > 0:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            __create_chain_and_run(fyle_credentials, in_progress_expenses, workspace_id, chain_tasks, fund_source)


def schedule_qbo_expense_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, fund_source: str):
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

        chain_tasks = []
        in_progress_expenses = []

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id, expense_group=expense_group, defaults={'status': 'ENQUEUED', 'type': 'CREATING_EXPENSE' if expense_group.fund_source == 'PERSONAL' else 'CREATING_DEBIT_CARD_EXPENSE'}
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_EXPENSE' if expense_group.fund_source == 'PERSONAL' else 'CREATING_DEBIT_CARD_EXPENSE'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain_tasks.append({
                'target': 'apps.quickbooks_online.tasks.create_qbo_expense',
                'expense_group': expense_group,
                'task_log_id': task_log.id,
                'last_export': last_export
            })

            # Don't include expenses with previous export state as ERROR and it's an auto import/export run
            if not (is_auto_export and expense_group.expenses.first().previous_export_state == 'ERROR'):
                in_progress_expenses.extend(expense_group.expenses.all())

        if len(chain_tasks) > 0:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            __create_chain_and_run(fyle_credentials, in_progress_expenses, workspace_id, chain_tasks, fund_source)


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
