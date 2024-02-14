import logging
from datetime import date, datetime
from typing import List

from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_q.models import Schedule
from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_integrations_platform_connector import PlatformConnector

from fyle_rest_auth.helpers import get_fyle_admin

from apps.fyle.tasks import async_create_expense_groups
from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import (
    FyleCredential,
    QBOCredential,
    Workspace,
    WorkspaceGeneralSettings,
    WorkspaceSchedule,
)
from apps.workspaces.queue import schedule_email_notification
from apps.users.models import User

from .actions import export_to_qbo

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def async_add_admins_to_workspace(workspace_id: int, current_user_id: str):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)

    users = []
    admins = platform.employees.get_admins()

    for admin in admins:
        # Skip current user since it is already added
        if current_user_id != admin['user_id']:
            users.append(User(email=admin['email'], user_id=admin['user_id'], full_name=admin['full_name']))

    if len(users):
        created_users = User.objects.bulk_create(users, batch_size=50)
        workspace = Workspace.objects.get(id=workspace_id)

        for user in created_users:
            workspace.user.add(user)


def schedule_sync(workspace_id: int, schedule_enabled: bool, hours: int, email_added: List, emails_selected: List):
    ws_schedule, _ = WorkspaceSchedule.objects.get_or_create(workspace_id=workspace_id)

    schedule_email_notification(workspace_id=workspace_id, schedule_enabled=schedule_enabled, hours=hours)

    if schedule_enabled:
        ws_schedule.enabled = schedule_enabled
        ws_schedule.start_datetime = datetime.now()
        ws_schedule.interval_hours = hours
        ws_schedule.emails_selected = emails_selected

        if email_added:
            ws_schedule.additional_email_options.append(email_added)

        schedule, _ = Schedule.objects.update_or_create(func='apps.workspaces.tasks.run_sync_schedule', args='{}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': hours * 60, 'next_run': datetime.now()})

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
    task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace_id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    fund_source = []
    if general_settings.reimbursable_expenses_object:
        fund_source.append('PERSONAL')
    if general_settings.corporate_credit_card_expenses_object:
        fund_source.append('CCC')

    async_create_expense_groups(workspace_id=workspace_id, fund_source=fund_source, task_log=task_log)

    if task_log.status == 'COMPLETE':
        export_to_qbo(workspace_id, 'AUTO')


def run_email_notification(workspace_id):
    expense_data = []
    expense_html = ''
    ws_schedule = WorkspaceSchedule.objects.get(workspace_id=workspace_id, enabled=True)

    task_logs = TaskLog.objects.filter(~Q(type__in=['CREATING_BILL_PAYMENT', 'FETCHING_EXPENSES']), workspace_id=workspace_id, status='FAILED')
    workspace = Workspace.objects.get(id=workspace_id)
    try:
        qbo = QBOCredential.get_active_qbo_credentials(workspace_id)
        errors = Error.objects.filter(workspace_id=workspace_id, is_resolved=False).order_by('id')[:10]
        for error in errors:
            if error.type == 'EMPLOYEE_MAPPING' or error.type == 'CATEGORY_MAPPING':
                html = '''<tr>
                            <td> Mapping Error </td>'''
            elif error.type == 'TAX_MAPPING':
                html = '''<tr>
                            <td> Tax Mapping Error </td>'''
            elif error.type == 'QBO_ERROR':
                html = '''<tr>
                        <td> QuickBooks Online Error </td>'''
            error_type = error.type.lower().title().replace('_', ' ')
            expense_data = list(expense_data)
            expense_data.append(error_type)
            if error.type == 'QBO_ERROR':
                html_data = (
                    '''<td>'''
                    + error.error_title
                    + '''</td>
                                <td>'''
                    + error.error_detail
                    + '''</td>
                            </tr>'''
                )
            else:
                html_data = (
                    '''<td>'''
                    + error_type
                    + '''</td>
                                <td style="padding-right: 8px">'''
                    + error.error_title
                    + '''</td>
                            </tr>'''
                )
            html = '{0} {1}'.format(html, html_data)
            expense_html = '{0} {1}'.format(expense_html, html)
        expense_data = set(expense_data)
        expense_data = ', '.join([str(data) for data in expense_data])
        for admin_email in ws_schedule.emails_selected:
            attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value=admin_email).first()

            admin_name = 'Admin'
            if attribute:
                admin_name = attribute.detail['full_name']
            else:
                for data in ws_schedule.additional_email_options:
                    if data['email'] == admin_email:
                        admin_name = data['name']

            if workspace.last_synced_at and workspace.ccc_last_synced_at:
                export_time = max(workspace.last_synced_at, workspace.ccc_last_synced_at)
            else:
                export_time = workspace.last_synced_at or workspace.ccc_last_synced_at

            if task_logs and (ws_schedule.error_count is None or len(task_logs) > ws_schedule.error_count):
                context = {
                    'name': admin_name,
                    'errors': len(task_logs),
                    'fyle_company': workspace.name,
                    'qbo_company': qbo.company_name,
                    'export_time': export_time.strftime("%d %b %Y | %H:%M"),
                    'year': date.today().year,
                    'app_url': "{0}/main/dashboard".format(settings.QBO_INTEGRATION_APP_URL),
                    'task_logs': mark_safe(expense_html),
                    'error_type': expense_data,
                }
                message = render_to_string("mail_template.html", context)

                mail = EmailMessage(subject="Export To QuickBooks Online Failed", body=message, from_email=settings.EMAIL, to=[admin_email])

                mail.content_subtype = "html"
                mail.send()

        ws_schedule.error_count = len(task_logs)
        ws_schedule.save()

    except QBOCredential.DoesNotExist:
        logger.info('QBO Credentials not found for workspace_id %s', workspace_id)


def async_update_fyle_credentials(fyle_org_id: str, refresh_token: str):
    fyle_credentials = FyleCredential.objects.filter(workspace__fyle_org_id=fyle_org_id).first()
    if fyle_credentials:
        fyle_credentials.refresh_token = refresh_token
        fyle_credentials.save()


def async_create_admin_subcriptions(workspace_id: int) -> None:
    """
    Create admin subscriptions
    :param workspace_id: workspace id
    :return: None
    """
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)
    payload = {
        'is_enabled': True,
        'webhook_url': '{}/workspaces/{}/fyle/exports/'.format(settings.API_URL, workspace_id)
    }
    platform.subscriptions.post(payload)


def async_update_workspace_name(workspace: Workspace, access_token: str):
    fyle_user = get_fyle_admin(access_token.split(' ')[1], None)
    org_name = fyle_user['data']['org']['name']

    workspace.name = org_name
    workspace.save()
