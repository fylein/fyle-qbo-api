from datetime import datetime, timedelta
from typing import List

from django_q.tasks import Chain, async_task
from django.db.models import Q
from django_q.models import Schedule

from apps.tasks.models import TaskLog

from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings
from apps.fyle.models import ExpenseGroup


def async_run_post_configration_triggers(
    workspace_general_settings: WorkspaceGeneralSettings,
):
    async_task(
        'apps.quickbooks_online.tasks.async_sync_accounts',
        int(workspace_general_settings.workspace_id),
    )


def schedule_bills_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule bills creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True)
            | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id,
            id__in=expense_group_ids,
            bill__id__isnull=True,
            exported_at__isnull=True,
        ).all()

        chain = Chain()

        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        chain.append('apps.fyle.tasks.sync_dimensions', fyle_credentials)

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={'status': 'ENQUEUED', 'type': 'CREATING_BILL'},
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_BILL'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain.append(
                'apps.quickbooks_online.tasks.create_bill',
                expense_group,
                task_log.id,
                last_export,
            )

        if chain.length() > 1:
            chain.run()


def schedule_cheques_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule cheque creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True)
            | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id,
            id__in=expense_group_ids,
            cheque__id__isnull=True,
            exported_at__isnull=True,
        ).all()

        chain = Chain()

        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        chain.append('apps.fyle.tasks.sync_dimensions', fyle_credentials)

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={'status': 'ENQUEUED', 'type': 'CREATING_CHECK'},
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_CHECK'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain.append(
                'apps.quickbooks_online.tasks.create_cheque',
                expense_group,
                task_log.id,
                last_export,
            )

        if chain.length() > 1:
            chain.run()


def schedule_journal_entry_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule journal_entry creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True)
            | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id,
            id__in=expense_group_ids,
            journalentry__id__isnull=True,
            exported_at__isnull=True,
        ).all()

        chain = Chain()

        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        chain.append('apps.fyle.tasks.sync_dimensions', fyle_credentials)

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={'status': 'ENQUEUED', 'type': 'CREATING_JOURNAL_ENTRY'},
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_JOURNAL_ENTRY'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain.append(
                'apps.quickbooks_online.tasks.create_journal_entry',
                expense_group,
                task_log.id,
                last_export,
            )

        if chain.length() > 1:
            chain.run()


def schedule_credit_card_purchase_creation(
    workspace_id: int, expense_group_ids: List[str]
):
    """
    Schedule credit card purchase creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True)
            | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id,
            id__in=expense_group_ids,
            creditcardpurchase__id__isnull=True,
            exported_at__isnull=True,
        ).all()

        chain = Chain()

        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        chain.append('apps.fyle.tasks.sync_dimensions', fyle_credentials)

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={
                    'status': 'ENQUEUED',
                    'type': 'CREATING_CREDIT_CARD_PURCHASE',
                },
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_CREDIT_CARD_PURCHASE'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain.append(
                'apps.quickbooks_online.tasks.create_credit_card_purchase',
                expense_group,
                task_log.id,
                last_export,
            )

        if chain.length() > 1:
            chain.run()


def schedule_qbo_expense_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule QBO expense creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True)
            | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id,
            id__in=expense_group_ids,
            qboexpense__id__isnull=True,
            exported_at__isnull=True,
        ).all()

        chain = Chain()

        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        chain.append('apps.fyle.tasks.sync_dimensions', fyle_credentials)

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={
                    'status': 'ENQUEUED',
                    'type': 'CREATING_EXPENSE'
                    if expense_group.fund_source == 'PERSONAL'
                    else 'CREATING_DEBIT_CARD_EXPENSE',
                },
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = (
                    'CREATING_EXPENSE'
                    if expense_group.fund_source == 'PERSONAL'
                    else 'CREATING_DEBIT_CARD_EXPENSE'
                )
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain.append(
                'apps.quickbooks_online.tasks.create_qbo_expense',
                expense_group,
                task_log.id,
                last_export,
            )

        if chain.length() > 1:
            chain.run()


def schedule_qbo_objects_status_sync(sync_qbo_to_fyle_payments, workspace_id):
    if sync_qbo_to_fyle_payments:
        start_datetime = datetime.now()
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.quickbooks_online.tasks.check_qbo_object_status',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime,
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.quickbooks_online.tasks.check_qbo_object_status',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_reimbursements_sync(sync_qbo_to_fyle_payments, workspace_id):
    if sync_qbo_to_fyle_payments:
        start_datetime = datetime.now() + timedelta(hours=12)
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.quickbooks_online.tasks.process_reimbursements',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime,
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.quickbooks_online.tasks.process_reimbursements',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()
