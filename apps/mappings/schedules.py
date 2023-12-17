from datetime import datetime
from django_q.models import Schedule
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_accounting_mappings.models import MappingSetting


def schedule_or_delete_fyle_import_tasks(workspace_general_settings: WorkspaceGeneralSettings, mapping_setting_instance: MappingSetting = None):
    """
    Schedule or delete Fyle import tasks based on the workspace_general_settings and mapping_settings.
    :param workspace_general_settings: Workspace workspace_general_settings Instance
    :param instance: Mapping Setting Instance
    :return: None
    """
    task_to_be_scheduled = None
    # Check if there is a task to be scheduled
    if mapping_setting_instance and mapping_setting_instance.import_to_fyle:
        task_to_be_scheduled = mapping_setting_instance

    if task_to_be_scheduled or workspace_general_settings.import_categories or workspace_general_settings.import_items:
        Schedule.objects.update_or_create(
            func='apps.mappings.queues.construct_tasks_and_chain_import_fields_to_fyle',
            args='{}'.format(workspace_general_settings.workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
        return

    import_fields_count = MappingSetting.objects.filter(
        import_to_fyle=True,
        workspace_id=workspace_general_settings.workspace_id,
        source_field__in=['PROJECT', 'COST_CENTER']
    ).count()

    custom_field_import_fields_count = MappingSetting.objects.filter(
        import_to_fyle=True,
        workspace_id=workspace_general_settings.workspace_id, 
        is_custom=True
    ).count()

    # If the import fields count is 0, delete the schedule
    if import_fields_count == 0 and custom_field_import_fields_count == 0\
        and not workspace_general_settings.import_categories and not workspace_general_settings.import_items:
        Schedule.objects.filter(
            func='apps.mappings.queues.construct_tasks_and_chain_import_fields_to_fyle',
            args='{}'.format(workspace_general_settings.workspace_id)
        ).delete()
