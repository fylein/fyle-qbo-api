from fyle_accounting_mappings.models import MappingSetting

from apps.mappings.queues import construct_tasks_and_chain_import_fields_to_fyle
from apps.workspaces.models import FeatureConfig


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


def test_construct_tasks_and_chain_import_fields_to_fyle_with_rabbitmq(mocker, db):
    """
    Test construct_tasks_and_chain_import_fields_to_fyle with RabbitMQ enabled
    This covers lines 64 and 72 in apps/mappings/queues.py
    """
    workspace_id = 3

    # Enable RabbitMQ for import
    feature_config = FeatureConfig.objects.get(workspace_id=workspace_id)
    feature_config.import_via_rabbitmq = True
    feature_config.save()

    # Mock the RabbitMQ publish function
    mock_publish = mocker.patch('apps.mappings.queues.publish_to_rabbitmq')

    MappingSetting.objects.filter(workspace_id=workspace_id).delete()
    MappingSetting.objects.create(
        source_field='PROJECT',
        destination_field='CUSTOMER',
        workspace_id=workspace_id,
        import_to_fyle=True,
        is_custom=False
    )

    construct_tasks_and_chain_import_fields_to_fyle(workspace_id)

    # Verify RabbitMQ publish was called
    mock_publish.assert_called_once()
    call_args = mock_publish.call_args
    assert call_args[1]['payload']['workspace_id'] == workspace_id
    assert call_args[1]['payload']['action'] == 'IMPORT.IMPORT_DIMENSIONS_TO_FYLE'
    assert call_args[1]['routing_key'] == 'IMPORT.*'
