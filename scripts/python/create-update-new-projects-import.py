from django.db import transaction
from datetime import datetime
from django_q.models import Schedule
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_accounting_mappings.models import MappingSetting

# TODO: take a backup of the schedules table before running this script

# grouping by workspace_id
existing_import_enabled_schedules = Schedule.objects.filter(
    func__in=['apps.mappings.tasks.auto_import_and_map_fyle_fields']
).values('args')

try:
    # Create/update new schedules in a transaction block
    with transaction.atomic():
        for schedule in existing_import_enabled_schedules:
            configuration = WorkspaceGeneralSettings.objects.get(workspace_id=schedule['args'])
            mapping_setting = MappingSetting.objects.filter(source_field='PROJECT', workspace_id=schedule['args'], import_to_fyle=True).first()
            
            if not configuration.import_categories and not configuration.import_vendors_as_merchants:
                schedule = Schedule.objects.filter(
                    func='apps.mappings.tasks.auto_import_and_map_fyle_fields',
                    args=schedule['args']
                ).first()
                schedule.delete()
            if mapping_setting:
                Schedule.objects.create(
                    func='apps.mappings.queues.construct_tasks_and_chain_import_fields_to_fyle',
                    args=schedule['args'],
                    schedule_type= Schedule.MINUTES,
                    minutes=24 * 60,
                    next_run=datetime.now()
                )
        project_count = MappingSetting.objects.filter(source_field='PROJECT', import_to_fyle=True).count()
        schedule_count = Schedule.objects.filter(func='apps.mappings.queues.construct_tasks_and_chain_import_fields_to_fyle').count()
        import_task_workspace_ids = WorkspaceGeneralSettings.objects.filter(import_categories=True, import_vendors_as_merchants=True).values_list('workspace_id', flat=True)
        combined_workspace_ids = []
        combined_workspace_ids.extend(import_task_workspace_ids)
        combined_workspace_ids = list(set(combined_workspace_ids))
        combined_workspace_ids_count = len(combined_workspace_ids)
        auto_import_schedule_count = Schedule.objects.filter(func='apps.mappings.tasks.auto_import_and_map_fyle_fields').count()
        print(f'project_count: {project_count}')
        print(f'schedule_count: {schedule_count}')
        print(f'combined_workspace_ids_count: {combined_workspace_ids_count}')
        print(f'auto_import_schedule_count: {auto_import_schedule_count}')
        # remove this sanity check after running this script
        raise Exception("This is a sanity check")

except Exception as e:
    print(e)
