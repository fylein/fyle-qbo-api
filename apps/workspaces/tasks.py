from datetime import datetime

from django.conf import settings

from apps.fyle.tasks import create_expense_groups
from apps.fyle.utils import FyleConnector
from apps.quickbooks_online.tasks import schedule_bills_creation
from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceSettings, WorkspaceSchedule, FyleCredential
from fyle_jobs import FyleJobsSDK


def schedule_sync(workspace_id: int, schedule_enabled: bool, hours: int, next_run: str, user: str):
    ws_settings, _ = WorkspaceSettings.objects.get_or_create(
        workspace_id=workspace_id
    )

    start_datetime = datetime.strptime(next_run, '%Y-%m-%dT%H:%M:00.000Z')

    if not ws_settings.schedule and schedule_enabled:
        schedule = WorkspaceSchedule.objects.create(
            enabled=schedule_enabled,
            interval_hours=hours,
            start_datetime=start_datetime
        )
        ws_settings.schedule = schedule

        created_job = create_schedule_job(
            workspace_id=workspace_id,
            schedule=schedule,
            user=user,
            start_datetime=start_datetime,
            hours=hours
        )

        ws_settings.schedule.fyle_job_id = created_job['id']
        ws_settings.schedule.save()

        ws_settings.save(update_fields=['schedule'])
    else:
        ws_settings.schedule.enabled = schedule_enabled
        ws_settings.schedule.start_datetime = start_datetime
        ws_settings.schedule.interval_hours = hours

        fyle_credentials = FyleCredential.objects.get(
            workspace_id=workspace_id)
        fyle_connector = FyleConnector(fyle_credentials.refresh_token)
        fyle_sdk_connection = fyle_connector.connection

        jobs = FyleJobsSDK(settings.FYLE_JOBS_URL, fyle_sdk_connection)
        if ws_settings.schedule.fyle_job_id:
            jobs.delete_job(ws_settings.schedule.fyle_job_id)

        if schedule_enabled:
            created_job = create_schedule_job(
                workspace_id=workspace_id,
                schedule=ws_settings.schedule,
                user=user,
                start_datetime=start_datetime,
                hours=hours
            )
            ws_settings.schedule.fyle_job_id = created_job['id']
        else:
            ws_settings.schedule.fyle_job_id = None

        ws_settings.schedule.save()

    return ws_settings


def create_schedule_job(workspace_id: int, schedule: WorkspaceSchedule, user: str,
                        start_datetime: datetime, hours: int):
    fyle_credentials = FyleCredential.objects.get(
        workspace_id=workspace_id)
    fyle_connector = FyleConnector(fyle_credentials.refresh_token)
    fyle_sdk_connection = fyle_connector.connection

    jobs = FyleJobsSDK(settings.FYLE_JOBS_URL, fyle_sdk_connection)

    created_job = jobs.trigger_interval(
        callback_url='{0}{1}'.format(
            settings.API_URL,
            '/workspaces/{0}/schedule/trigger/'.format(workspace_id)
        ),
        callback_method='POST',
        object_id=schedule.id,
        job_description='Fetch expenses: Workspace id - {0}, user - {1}'.format(
            workspace_id, user
        ),
        start_datetime=start_datetime.strftime('%Y-%m-%d %H:%M:00.00'),
        hours=hours
    )
    return created_job


def run_sync_schedule(workspace_id, user: str):
    """
    Run schedule
    :param user: user email
    :param workspace_id: workspace id
    :return: None
    """
    task_log = TaskLog.objects.create(
        workspace_id=workspace_id,
        type='FETCHING_EXPENSES',
        status='IN_PROGRESS'
    )

    task_log: TaskLog = create_expense_groups(
        workspace_id=workspace_id, state=['PAYMENT_PROCESSING'],
        export_non_reimbursable=False,
        task_log=task_log
    )

    if task_log.status == 'COMPLETE':
        schedule_bills_creation(workspace_id=workspace_id, expense_group_ids=[], user=user)
