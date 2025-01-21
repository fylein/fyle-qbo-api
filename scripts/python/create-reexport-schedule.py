from datetime import datetime

from django_q.models import Schedule

schedule, _ = Schedule.objects.create(func='apps.internal.actions.re_export_stuck_exports', args=None, defaults={'schedule_type': Schedule.MINUTES, 'minutes': 3 * 60, 'next_run': datetime.now()})
