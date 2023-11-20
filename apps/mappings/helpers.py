from datetime import datetime

from django_q.models import Schedule
from fyle_accounting_mappings.models import MappingSetting

from apps.workspaces.models import WorkspaceGeneralSettings


def schedule_or_delete_fyle_import_tasks(configuration: WorkspaceGeneralSettings):
    """
    :param configuration: WorkspaceGeneralSettings Instance
    :return: None
    """
    if configuration.import_categories or configuration.import_items or configuration.import_vendors_as_merchants:
        start_datetime = datetime.now()
        Schedule.objects.update_or_create(func='apps.mappings.tasks.auto_import_and_map_fyle_fields', args='{}'.format(configuration.workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': 24 * 60, 'next_run': start_datetime})
    elif not configuration.import_categories and not configuration.import_items and not configuration.import_vendors_as_merchants:
        Schedule.objects.filter(func='apps.mappings.tasks.auto_import_and_map_fyle_fields', args='{}'.format(configuration.workspace_id)).delete()


def get_auto_sync_permission(mapping_setting: MappingSetting):
    """
    Get the auto sync permission
    :return: bool
    """
    is_auto_sync_status_allowed = False
    if (mapping_setting.destination_field == 'CUSTOMER' and mapping_setting.source_field == 'PROJECT') or mapping_setting.source_field == 'CATEGORY':
        is_auto_sync_status_allowed = True

    return is_auto_sync_status_allowed
