import random
from datetime import datetime, timedelta

from django.db import transaction
from django_q.models import Schedule

from apps.workspaces.models import WorkspaceGeneralSettings

existing_import_enabled_schedules = Schedule.objects.filter(
    func__in=['apps.mappings.tasks.auto_create_tax_codes_mappings', 'apps.mappings.tasks.auto_import_and_map_fyle_fields']
).values('args')

try:
    with transaction.atomic():
        for schedule in existing_import_enabled_schedules:
            random_number = random.randint(1, 23)
            workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=schedule['args'])
            if workspace_general_settings.import_tax_codes or workspace_general_settings.import_vendors_as_merchants:
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
                if workspace_general_settings.import_tax_codes:
                    # deleting the old tax schedule
                    Schedule.objects.filter(
                        func='apps.mappings.tasks.auto_create_tax_codes_mappings',
                        args=schedule['args']
                    ).delete()
                if workspace_general_settings.import_vendors_as_merchants:
                    # deleting the old merchants schedule
                    Schedule.objects.filter(
                        func='apps.mappings.tasks.auto_import_and_map_fyle_fields',
                        args=schedule['args']
                    ).delete()
        # remove this sanity check after running this script
        raise Exception("This is a sanity check")
except Exception as e:
    print(e)


# Run this in sql
# select * from django_q_schedule where func in ('apps.mappings.tasks.auto_create_tax_codes_mappings', 'apps.mappings.tasks.auto_import_and_map_fyle_fields');
# --rows should be 0
