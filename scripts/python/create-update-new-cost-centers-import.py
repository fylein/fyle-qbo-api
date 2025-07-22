import random
from datetime import datetime, timedelta

from django.db import transaction
from django_q.models import Schedule
from fyle_accounting_mappings.models import MappingSetting

existing_import_enabled_schedules = Schedule.objects.filter(
    func__in=['apps.mappings.tasks.auto_create_cost_center_mappings']
).values('args')

try:
    with transaction.atomic():
        for schedule in existing_import_enabled_schedules:
            random_number = random.randint(1, 23)
            mapping_setting = MappingSetting.objects.filter(source_field='COST_CENTER', workspace_id=schedule['args'], import_to_fyle=True).first()
            if mapping_setting:
                print('Creating schedule for workspace_id: ', schedule['args'])
                # adding the new schedule
                Schedule.objects.update_or_create(
                    func='apps.mappings.queues.construct_tasks_and_chain_import_fields_to_fyle',
                    args=schedule['args'],
                    defaults={
                        'schedule_type': Schedule.MINUTES,
                        'minutes':24 * 60,
                        'next_run':datetime.now() + timedelta(hours=random_number)
                    }
                )
                # deleting the old schedule
                Schedule.objects.filter(
                    func='apps.mappings.tasks.auto_create_cost_center_mappings',
                    args=schedule['args']
                ).delete()
        # remove this sanity check after running this script
        raise Exception("This is a sanity check")
except Exception as e:
    print(e)


# Run this in sql
# select * from django_q_schedule where func = 'apps.mappings.tasks.auto_create_cost_center_mappings';
# --rows should be 0
# If not check the workspace_id and delete the row
# delete from django_q_schedule where func = 'apps.mappings.tasks.auto_create_cost_center_mappings' and args = 'workspace_id';
