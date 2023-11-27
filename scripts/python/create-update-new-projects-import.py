from django.db import transaction
from datetime import datetime
from django_q.models import Schedule
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_accounting_mappings.models import MappingSetting
existing_import_enabled_schedules = Schedule.objects.filter(
    func__in=['apps.mappings.tasks.auto_import_and_map_fyle_fields']
).values('args')
try:
    # Create/update new schedules in a transaction block
    with transaction.atomic():
        for schedule in existing_import_enabled_schedules:
            configuration = WorkspaceGeneralSettings.objects.get(workspace_id=schedule['args'])
            mapping_setting = MappingSetting.objects.filter(source_field='PROJECT', workspace_id=schedule['args'], import_to_fyle=True).first()
            if not configuration.import_categories and not configuration.import_items and not configuration.import_vendors_as_merchants:
                print('Deleting schedule for workspace_id: ', schedule['args'])
                Schedule.objects.get(
                    func='apps.mappings.tasks.auto_import_and_map_fyle_fields',
                    args=schedule['args']
                ).delete()
            if mapping_setting:
                print('Creating schedule for workspace_id: ', schedule['args'])
                Schedule.objects.create(
                    func='apps.mappings.queues.construct_tasks_and_chain_import_fields_to_fyle',
                    args=schedule['args'],
                    schedule_type= Schedule.MINUTES,
                    minutes=24 * 60,
                    next_run=datetime.now()
                )
        # remove this sanity check after running this script
        raise Exception("This is a sanity check")
except Exception as e:
    print(e)
