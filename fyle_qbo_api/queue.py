from datetime import datetime, timedelta
from typing import List


from django_q.models import Schedule
from django_q.tasks import Chain
from django.db.models import Q

from fyle_accounting_mappings.models import MappingSetting

from apps.tasks.models import TaskLog
from apps.mappings.models import GeneralMapping
from apps.workspaces.models import WorkspaceGeneralSettings, FyleCredential
from apps.fyle.models import ExpenseGroup


def schedule_cost_centers_creation(import_to_fyle, workspace_id):
    if import_to_fyle:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_cost_center_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_cost_center_mappings',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def schedule_fyle_attributes_creation(workspace_id: int):
    mapping_settings = MappingSetting.objects.filter(
        is_custom=True, import_to_fyle=True, workspace_id=workspace_id
    ).all()
    if mapping_settings:
        schedule, _ = Schedule.objects.get_or_create(
            func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
            args='{0}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now() + timedelta(hours=24)
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
            args='{0}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def schedule_tax_groups_creation(import_tax_codes, workspace_id):
    if import_tax_codes:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_tax_codes_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_tax_codes_mappings',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_auto_map_employees(employee_mapping_preference: str, workspace_id: int):
    if employee_mapping_preference:
        start_datetime = datetime.now()

        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.async_auto_map_employees',
            args='{0}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_map_employees',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def schedule_auto_map_ccc_employees(workspace_id: int):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    if general_settings.auto_map_employees and general_settings.corporate_credit_card_expenses_object != 'BILL':
        start_datetime = datetime.now()

        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.async_auto_map_ccc_account',
            args='{0}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_map_ccc_account',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def schedule_bill_payment_creation(sync_fyle_to_qbo_payments, workspace_id):
    general_mappings: GeneralMapping = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    if general_mappings:
        if sync_fyle_to_qbo_payments and general_mappings.bill_payment_account_id:
            start_datetime = datetime.now()
            schedule, _ = Schedule.objects.update_or_create(
                func='apps.quickbooks_online.tasks.create_bill_payment',
                args='{}'.format(workspace_id),
                defaults={
                    'schedule_type': Schedule.MINUTES,
                    'minutes': 24 * 60,
                    'next_run': start_datetime
                }
            )
    if not sync_fyle_to_qbo_payments:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.quickbooks_online.tasks.create_bill_payment',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def schedule_qbo_objects_status_sync(sync_qbo_to_fyle_payments, workspace_id):
    if sync_qbo_to_fyle_payments:
        start_datetime = datetime.now()
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.quickbooks_online.tasks.check_qbo_object_status',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.quickbooks_online.tasks.check_qbo_object_status',
            args='{}'.format(workspace_id)
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
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.quickbooks_online.tasks.process_reimbursements',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def schedule_email_notification(workspace_id: int, schedule_enabled: bool, hours: int):
    if schedule_enabled:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.workspaces.tasks.run_email_notification',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': hours * 60,
                'next_run': datetime.now() + timedelta(minutes=10)
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.workspaces.tasks.run_email_notification',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()

def schedule_bills_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule bills creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, bill__id__isnull=True, exported_at__isnull=True
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
                    'type': 'CREATING_BILL'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_BILL'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain.append('apps.quickbooks_online.tasks.create_bill', expense_group, task_log.id, last_export)

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
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, cheque__id__isnull=True, exported_at__isnull=True
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
                    'type': 'CREATING_CHECK'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_CHECK'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain.append('apps.quickbooks_online.tasks.create_cheque', expense_group, task_log.id, last_export)

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
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, qboexpense__id__isnull=True, exported_at__isnull=True
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
                    'type': 'CREATING_EXPENSE' if expense_group.fund_source == 'PERSONAL' else 
                    'CREATING_DEBIT_CARD_EXPENSE'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_EXPENSE' if expense_group.fund_source == 'PERSONAL' else \
                'CREATING_DEBIT_CARD_EXPENSE'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain.append('apps.quickbooks_online.tasks.create_qbo_expense', expense_group, task_log.id, last_export)

        if chain.length() > 1:
            chain.run()

def schedule_credit_card_purchase_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule credit card purchase creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, creditcardpurchase__id__isnull=True,
            exported_at__isnull=True
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
                    'type': 'CREATING_CREDIT_CARD_PURCHASE'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_CREDIT_CARD_PURCHASE'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain.append('apps.quickbooks_online.tasks.create_credit_card_purchase', expense_group, task_log.id, 
                         last_export)

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
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, journalentry__id__isnull=True, 
            exported_at__isnull=True
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
                    'type': 'CREATING_JOURNAL_ENTRY'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.type = 'CREATING_JOURNAL_ENTRY'
                task_log.status = 'ENQUEUED'
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain.append('apps.quickbooks_online.tasks.create_journal_entry', expense_group, task_log.id, last_export)

        if chain.length() > 1:
            chain.run()
