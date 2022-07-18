import time
from datetime import datetime, timedelta, date
from typing import List

from django.conf import settings
from django.db.models import Q

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django_q.models import Schedule
from django.utils.safestring import mark_safe

from apps.fyle.tasks import async_create_expense_groups
from apps.fyle.models import Expense, ExpenseGroup
from apps.fyle.serializers import ExpenseSerializer
from apps.quickbooks_online.tasks import schedule_bills_creation, schedule_cheques_creation, \
    schedule_journal_entry_creation, schedule_credit_card_purchase_creation, schedule_qbo_expense_creation
from apps.tasks.models import TaskLog
from apps.workspaces.models import User, Workspace, WorkspaceSchedule, WorkspaceGeneralSettings, LastExportDetail, QBOCredential
from fyle_accounting_mappings.models import ExpenseAttribute


def schedule_email_notification(workspace_id: int, schedule_enabled: bool, hours: int):
    if schedule_enabled:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.workspaces.tasks.run_email_notification',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 5,
                'next_run': datetime.now() + timedelta(minutes=1)
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.workspaces.tasks.run_email_notification',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def schedule_sync(workspace_id: int, schedule_enabled: bool, hours: int, email_added: List, emails_selected: List):
    ws_schedule, _ = WorkspaceSchedule.objects.get_or_create(
        workspace_id=workspace_id
    )

    schedule_email_notification(workspace_id=workspace_id, schedule_enabled=schedule_enabled, hours=hours)

    if schedule_enabled:
        ws_schedule.enabled = schedule_enabled
        ws_schedule.start_datetime = datetime.now()
        ws_schedule.interval_hours = hours
        ws_schedule.emails_selected = emails_selected
        
        if email_added:
            ws_schedule.additional_email_options.append(email_added)


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

    elif not schedule_enabled and ws_schedule.schedule:
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

    fund_source = []
    if general_settings.reimbursable_expenses_object:
        fund_source.append('PERSONAL')
    if general_settings.corporate_credit_card_expenses_object:
        fund_source.append('CCC')

    async_create_expense_groups(
        workspace_id=workspace_id, fund_source=fund_source, task_log=task_log
    )

    if task_log.status == 'COMPLETE':
        export_to_qbo(workspace_id, 'AUTO')


def export_to_qbo(workspace_id, export_mode=None):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    last_export_detail.last_exported_at = datetime.now()
    last_export_detail.export_mode = export_mode or 'MANUAL'
    last_export_detail.save()

    if general_settings.reimbursable_expenses_object:

        expense_group_ids = ExpenseGroup.objects.filter(
            fund_source='PERSONAL', exported_at__isnull=True
        ).values_list('id', flat=True)

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
        expense_group_ids = ExpenseGroup.objects.filter(
            fund_source='CCC', exported_at__isnull=True
        ).values_list('id', flat=True)

        if general_settings.corporate_credit_card_expenses_object == 'JOURNAL ENTRY':
            schedule_journal_entry_creation(
                workspace_id=workspace_id, expense_group_ids=expense_group_ids
            )

        elif general_settings.corporate_credit_card_expenses_object == 'CREDIT CARD PURCHASE':
            schedule_credit_card_purchase_creation(
                workspace_id=workspace_id, expense_group_ids=expense_group_ids
            )

        elif general_settings.corporate_credit_card_expenses_object == 'DEBIT CARD EXPENSE':
            schedule_qbo_expense_creation(
                workspace_id=workspace_id, expense_group_ids=expense_group_ids
            )

        elif general_settings.corporate_credit_card_expenses_object == 'BILL':
            schedule_bills_creation(
                workspace_id=workspace_id, expense_group_ids=expense_group_ids
            )

def run_email_notification(workspace_id):
    expense_data=''
    ws_schedule, _ = WorkspaceSchedule.objects.get_or_create(
        workspace_id=workspace_id
    )

    task_logs = TaskLog.objects.filter(
        ~Q(type__in=['CREATING_REIMBURSEMENT', 'FETCHING_EXPENSES', 'CREATING_AP_PAYMENT']),
        workspace_id=workspace_id,
        status='FAILED'
    )
    workspace = Workspace.objects.get(id=workspace_id)
    admin_data = WorkspaceSchedule.objects.get(workspace_id=workspace_id)
    qbo = QBOCredential.objects.get(workspace=workspace)
    for task_log in task_logs:
        expense_group = ExpenseGroup.objects.get(workspace_id=workspace_id, pk=task_log.expense_group_id)
        expenses = Expense.objects.filter(id__in=expense_group.expenses.values_list('id', flat=True)).order_by('-updated_at')
        expenses = ExpenseSerializer(expenses, many=True).data
        for log in task_log.detail:
            for expense in expenses:
                expense = dict(expense)
                link = 'https://app.fyle.tech/app/admin/#/reports/' + expense['report_id'] + 'org_id=' + expense['org_id']
                html = '''<tr>
                    <td>''' + expense["claim_number"] + '''</td>
                    <td>''' + expense["expense_number"] + '''</td>
                    <td>''' + log['message'] + '''</td>
                    <td>
                        <a href = "''' + link + '''">
                        <img src="https://raw.githubusercontent.com/fylein/fyle-qbo-api/qbo-email-notification1/apps/workspaces/templates/images/redirect-icon.png" width="18" height="18">
                        </a>
                    </td>
                    </tr>'''
                expense_data = expense_data + html
            
    if ws_schedule.enabled:
        for admin_email in admin_data.emails_selected:
            attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value=admin_email).first()

            if attribute:
                admin_name = attribute.detail['full_name']
            else:
                for data in admin_data.additional_email_options:
                    if data['email'] == admin_email:
                        admin_name = data['name']

            if task_logs and (ws_schedule.error_count is None or len(task_logs) > ws_schedule.error_count):
                context = {
                    'name': admin_name,
                    'errors': len(task_logs),
                    'fyle_company': workspace.name,
                    'qbo_company': qbo.company_name,
                    'workspace_id': workspace_id,
                    'export_time': workspace.last_synced_at.date(),
                    'year': date.today().year,
                    'app_url': "{0}/workspaces/{1}/expense_groups".format(settings.FYLE_APP_URL, workspace_id),
                    'task_logs': mark_safe(expense_data)
                    }
                message = render_to_string("mail_template.html", context)

                mail = EmailMessage(
                    subject="Export To QuickBooks Online Failed",
                    body=message,
                    from_email=settings.EMAIL,
                    to=[admin_email],
                )

                mail.content_subtype = "html"
                mail.send()

        ws_schedule.error_count = len(task_logs)
        ws_schedule.save()

