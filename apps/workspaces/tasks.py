from datetime import datetime
import email
from typing import List
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from django_q.models import Schedule

from apps.fyle.models import ExpenseGroup
from apps.fyle.tasks import async_create_expense_groups
from apps.quickbooks_online.tasks import schedule_bills_creation, schedule_cheques_creation, \
    schedule_journal_entry_creation, schedule_credit_card_purchase_creation, schedule_qbo_expense_creation
from apps.tasks.models import TaskLog
from apps.workspaces.models import Workspace, WorkspaceSchedule, WorkspaceGeneralSettings

User = get_user_model()

def schedule_sync(workspace_id: int, schedule_enabled: bool, hours: int, emails: List):
    ws_schedule, _ = WorkspaceSchedule.objects.get_or_create(
        workspace_id=workspace_id
    )

    if schedule_enabled:
        ws_schedule.enabled = schedule_enabled
        ws_schedule.start_datetime = datetime.now()
        ws_schedule.interval_hours = hours
        ws_schedule.emails = emails

        schedule, _ = Schedule.objects.update_or_create(
            func='apps.workspaces.tasks.run_sync_schedule',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': hours * 60,
                'next_run': datetime.now()
            }
        )
        ws_schedule.schedule = schedule

        ws_schedule.save()

    elif not schedule_enabled:
        schedule = ws_schedule.schedule
        ws_schedule.enabled = schedule_enabled
        ws_schedule.schedule = None
        ws_schedule.save()
        schedule.delete()

    return ws_schedule


def run_sync_schedule(workspace_id):
    """
    Run schedule
    :param workspace_id: workspace id
    :return: None
    """
    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    fund_source = ['PERSONAL']
    if general_settings.corporate_credit_card_expenses_object:
        fund_source.append('CCC')
    if general_settings.reimbursable_expenses_object:
        async_create_expense_groups(
            workspace_id=workspace_id, fund_source=fund_source, task_log=task_log
        )

    if task_log.status == 'COMPLETE':
        all_expense_group_ids = []

        if general_settings.reimbursable_expenses_object:

            expense_group_ids = ExpenseGroup.objects.filter(fund_source='PERSONAL', workspace_id=workspace_id).values_list('id', flat=True)

            if general_settings.reimbursable_expenses_object == 'BILL':
                schedule_bills_creation(
                    workspace_id=workspace_id, expense_group_ids=expense_group_ids
                )

            elif general_settings.reimbursable_expenses_object == 'EXPENSE':
                schedule_qbo_expense_creation(
                    workspace_id=workspace_id, expense_group_ids=expense_group_ids
                )

            elif general_settings.reimbursable_expenses_object == 'CHECK':
                schedule_cheques_creation(
                    workspace_id=workspace_id, expense_group_ids=expense_group_ids
                )

            elif general_settings.reimbursable_expenses_object == 'JOURNAL ENTRY':
                schedule_journal_entry_creation(
                    workspace_id=workspace_id, expense_group_ids=expense_group_ids
                )

        if general_settings.corporate_credit_card_expenses_object:
            expense_group_ids = ExpenseGroup.objects.filter(fund_source='CCC', workspace_id=workspace_id).values_list('id', flat=True)

            if general_settings.corporate_credit_card_expenses_object == 'JOURNAL ENTRY':
                schedule_journal_entry_creation(
                    workspace_id=workspace_id, expense_group_ids=expense_group_ids
                )

            elif general_settings.corporate_credit_card_expenses_object == 'CREDIT CARD PURCHASE':
                schedule_credit_card_purchase_creation(
                    workspace_id=workspace_id, expense_group_ids=expense_group_ids
                )

            elif general_settings.corporate_credit_card_expenses_object == 'BILL':
                schedule_bills_creation(
                    workspace_id=workspace_id, expense_group_ids=expense_group_ids
                )


def run_schedule_email_notification(workspace_id):

    ws_schedule, _ = WorkspaceSchedule.objects.get_or_create(
        workspace_id=workspace_id
    )

    admin_emails = []
    if ws_schedule.enabled:
        task_logs = TaskLog.objects.filter(workspace_id=workspace_id, status='FAILED')
        workspace_admins = Workspace.objects.filter(pk=workspace_id).values_list('user', flat=True)

        for admin_id in workspace_admins:
            user_email = User.objects.get(id=admin_id).email
            admin_emails.append(user_email)

        if ws_schedule.total_errors is None or len(task_logs) > ws_schedule.total_errors:
            context = {
                'name': 'Elon Musk',
                'errors': len(task_logs),
                'task_log': task_logs[0].detail
            }

            ws_schedule.total_errors = len(task_logs)
            ws_schedule.save()

            message = render_to_string("mail_template.html", context)

            mail = EmailMessage(
                subject="Export To Netsuite Failed",
                body=message,
                from_email='nilesh.p@fyle.in',
                to=['nileshpant112@gmail.com'],
            )

            mail.content_subtype = "html"
            mail.send()
