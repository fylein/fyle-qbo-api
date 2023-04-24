from datetime import datetime

from django_q.models import Schedule

from fyle_accounting_mappings.models import MappingSetting, Mapping
from apps.workspaces.models import WorkspaceGeneralSettings


def schedule_or_delete_fyle_import_tasks(configuration: WorkspaceGeneralSettings):
    """
    :param configuration: WorkspaceGeneralSettings Instance
    :return: None
    """
    project_mapping = MappingSetting.objects.filter(source_field='PROJECT', workspace_id=configuration.workspace_id).first()
    if configuration.import_categories or (project_mapping and project_mapping.import_to_fyle) or configuration.import_vendors_as_merchants:
        start_datetime = datetime.now()
        Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_import_and_map_fyle_fields',
            args='{}'.format(configuration.workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    elif not configuration.import_categories and not (project_mapping and project_mapping.import_to_fyle) and not configuration.import_vendors_as_merchants:
        Schedule.objects.filter(
            func='apps.mappings.tasks.auto_import_and_map_fyle_fields',
            args='{}'.format(configuration.workspace_id)
        ).delete()

   
def delete_items_mappings(configuration: WorkspaceGeneralSettings):
    """
    Delete all the mappings when import_items is set to false
    :param configuration: WorkspaceGeneralSettings Instance
    :return: None
    """

    if not configuration.import_items:
        Mapping.objects.filter(
            workspace_id=configuration.workspace_id,
            source_type='CATEGORY',
            destination_type='ACCOUNT',
            destination__display_name='Item').delete()

    return []
