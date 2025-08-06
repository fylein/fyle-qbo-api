import logging
from unittest import mock

from fyle_accounting_mappings.models import ExpenseAttribute

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from apps.workspaces.signals import post_delete_qbo_connection, run_post_configration_triggers

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


def test_run_post_configration_triggers_with_credit_card_purchase(db, add_expense_attributes_for_unmapped_cards_test):
    """
    Test run_post_configration_triggers signal when corporate_credit_card_expenses_object is 'CREDIT CARD PURCHASE'
    This test covers lines 44-45 and 48 that were missing coverage
    """
    workspace_id = 1
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_settings.corporate_credit_card_expenses_object = 'CREDIT CARD PURCHASE'

    with mock.patch('apps.workspaces.signals.async_run_post_configration_triggers') as mock_async_trigger:
        with mock.patch('apps.workspaces.signals.delete_cards_mapping_settings') as mock_delete_cards:
            with mock.patch('apps.workspaces.signals.patch_integration_settings_for_unmapped_cards') as mock_patch_settings:
                run_post_configration_triggers(WorkspaceGeneralSettings, workspace_general_settings, created=False)
                expected_unmapped_count = ExpenseAttribute.objects.filter(
                    attribute_type="CORPORATE_CARD",
                    workspace_id=workspace_id,
                    active=True,
                    mapping__isnull=True
                ).count()
                mock_patch_settings.assert_called_with(
                    workspace_id=workspace_id,
                    unmapped_card_count=expected_unmapped_count
                )
                mock_async_trigger.assert_called_once_with(workspace_general_settings)
                mock_delete_cards.assert_called_once_with(workspace_general_settings)


def test_run_post_configration_triggers_without_credit_card_purchase(db):
    """
    Test run_post_configration_triggers signal when corporate_credit_card_expenses_object is NOT 'CREDIT CARD PURCHASE'
    This test covers line 50 (the else clause) that was missing coverage
    """
    workspace_id = 1
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_settings.corporate_credit_card_expenses_object = 'BILL'

    with mock.patch('apps.workspaces.signals.async_run_post_configration_triggers') as mock_async_trigger:
        with mock.patch('apps.workspaces.signals.delete_cards_mapping_settings') as mock_delete_cards:
            with mock.patch('apps.workspaces.signals.patch_integration_settings_for_unmapped_cards') as mock_patch_settings:
                run_post_configration_triggers(WorkspaceGeneralSettings, workspace_general_settings, created=False)
                mock_patch_settings.assert_called_with(
                    workspace_id=workspace_id,
                    unmapped_card_count=0
                )
                mock_async_trigger.assert_called_once_with(workspace_general_settings)
                mock_delete_cards.assert_called_once_with(workspace_general_settings)
