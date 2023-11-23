from apps.mappings.queues import construct_tasks_and_chain_import_fields_to_fyle
from fyle_accounting_mappings.models import MappingSetting


def test_construct_tasks_and_chain_import_fields_to_fyle(db):
    workspace_id = 3
    MappingSetting.objects.filter(workspace_id=workspace_id).delete()
    MappingSetting.objects.create(
        source_field='PROJECT',
        destination_field='CUSTOMER',
        workspace_id=workspace_id,
        import_to_fyle=True,
        is_custom=False
    )

    construct_tasks_and_chain_import_fields_to_fyle(workspace_id)
