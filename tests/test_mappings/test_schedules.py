from django_q.models import Schedule
from fyle_accounting_mappings.models import MappingSetting

from apps.mappings.schedules import schedule_or_delete_fyle_import_tasks
from apps.workspaces.models import WorkspaceGeneralSettings


def test_schedule_creation(db):
    workspace_id = 3

    # Test schedule projects creation
    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    configuration.import_categories = True
    configuration.import_projects = True
    configuration.import_vendors_as_merchants = True
    configuration.import_tax_codes = True
    configuration.save()

    MappingSetting.objects.filter(workspace_id=workspace_id).delete()
    mapping_settings = [
        {
            'source_field': 'PROJECT',
            'destination_field': 'CUSTOMER',
            'import_to_fyle': True,
            'is_custom': False
        }
    ]

    schedule_or_delete_fyle_import_tasks(configuration, mapping_settings)

    schedule = Schedule.objects.filter(
        func='apps.mappings.queues.construct_tasks_and_chain_import_fields_to_fyle',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule.func == 'apps.mappings.queues.construct_tasks_and_chain_import_fields_to_fyle'
    assert schedule.args == '3'
