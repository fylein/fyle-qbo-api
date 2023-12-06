from django.db import transaction
import random
from datetime import datetime, timedelta
from django_q.models import Schedule
from apps.workspaces.models import WorkspaceGeneralSettings
existing_import_enabled_schedules = Schedule.objects.filter(
    func__in=['apps.mappings.tasks.auto_import_and_map_fyle_fields']
).values('args')
try:
    # Create/update new schedules in a transaction block
    with transaction.atomic():
        for schedule in existing_import_enabled_schedules:
            random_number = random.randint(1, 23)
            configuration = WorkspaceGeneralSettings.objects.get(workspace_id=schedule['args'])
            if not configuration.import_vendors_as_merchants:
                print('Deleting schedule for workspace_id: ', schedule['args'])
                Schedule.objects.get(
                    func='apps.mappings.tasks.auto_import_and_map_fyle_fields',
                    args=schedule['args']
                ).delete()
            if configuration.import_categories or configuration.import_items:
                print('Creating schedule for workspace_id: ', schedule['args'])
                Schedule.objects.create(
                    func='apps.mappings.queues.construct_tasks_and_chain_import_fields_to_fyle',
                    args=schedule['args'],
                    schedule_type= Schedule.MINUTES,
                    minutes=24 * 60,
                    next_run=datetime.now() + timedelta(hours=random_number)
                )
        # remove this sanity check after running this script
        raise Exception("This is a sanity check")
except Exception as e:
    print(e)
