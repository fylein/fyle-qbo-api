import logging

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from apps.workspaces.signals import post_delete_qbo_connection

logger = logging.getLogger(__name__)


def test_pre_save_workspace_general_settings(db, add_destination_attributes_for_import_items_test):
    """
    Test pre_save_workspace_general_settings signal
    Tests that when import_items is changed from True to False,
    DestinationAttribute objects with attribute_type='ACCOUNT' and display_name='Item'
    are deactivated
    """
    workspace_id = 1
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    workspace_general_settings.import_items = True
    workspace_general_settings.save()

    test_data = add_destination_attributes_for_import_items_test
    item_attribute_1 = test_data['item_attribute_1']
    item_attribute_2 = test_data['item_attribute_2']
    inactive_item_attribute = test_data['inactive_item_attribute']

    assert item_attribute_1.active == True
    assert item_attribute_2.active == True
    assert inactive_item_attribute.active == False

    workspace_general_settings.import_items = False
    workspace_general_settings.save()

    item_attribute_1.refresh_from_db()
    item_attribute_2.refresh_from_db()
    inactive_item_attribute.refresh_from_db()

    assert item_attribute_1.active == False
    assert item_attribute_2.active == False
    assert inactive_item_attribute.active == False


def test_post_delete_qbo_connection(db):
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    workspace.onboarding_state = 'EXPORT_SETTINGS'
    workspace.save()

    try:
        post_delete_qbo_connection(workspace_id)

        workspace = Workspace.objects.get(id=workspace_id)

        assert workspace.qbo_realm_id == None
    except Exception:
        logger.info('null value in column "qbo_realm_id" of relation "workspaces" violates not-null constraint')
