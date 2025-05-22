from datetime import datetime, timedelta

from django_q.models import Schedule


def schedule_email_notification(workspace_id: int, schedule_enabled: bool, hours: int):
    if schedule_enabled and hours:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.workspaces.tasks.run_email_notification', cluster='import', args='{}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': hours * 60, 'next_run': datetime.now() + timedelta(minutes=10)}
        )
    else:
        schedule: Schedule = Schedule.objects.filter(func='apps.workspaces.tasks.run_email_notification', args='{}'.format(workspace_id)).first()

        if schedule:
            schedule.delete()
