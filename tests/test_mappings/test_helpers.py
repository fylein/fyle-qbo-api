from unittest import mock

import pytest

from apps.mappings.helpers import patch_corporate_card_integration_settings
from apps.workspaces.models import WorkspaceGeneralSettings


@pytest.mark.django_db()
def test_patch_corporate_card_integration_settings(test_connection):
    """
    Test patch_corporate_card_integration_settings helper - tests all conditions
    """
    workspace_id = 3
    workspace_general_settings, _ = WorkspaceGeneralSettings.objects.get_or_create(
        workspace_id=workspace_id,
        defaults={'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'}
    )
    workspace_general_settings.corporate_credit_card_expenses_object = 'CREDIT CARD PURCHASE'
    workspace_general_settings.save()

    with mock.patch('apps.mappings.helpers.patch_integration_settings_for_unmapped_cards') as mock_patch:
        patch_corporate_card_integration_settings(workspace_id=workspace_id)
        mock_patch.assert_called_once()
        assert mock_patch.call_args[1]['workspace_id'] == workspace_id
        assert 'unmapped_card_count' in mock_patch.call_args[1]

    workspace_general_settings.corporate_credit_card_expenses_object = 'DEBIT CARD EXPENSE'
    workspace_general_settings.save()

    with mock.patch('apps.mappings.helpers.patch_integration_settings_for_unmapped_cards') as mock_patch:
        patch_corporate_card_integration_settings(workspace_id=workspace_id)
        mock_patch.assert_called_once()

    workspace_general_settings.corporate_credit_card_expenses_object = 'BILL'
    workspace_general_settings.save()
    with mock.patch('apps.mappings.helpers.patch_integration_settings_for_unmapped_cards') as mock_patch:
        patch_corporate_card_integration_settings(workspace_id=workspace_id)
        mock_patch.assert_not_called()
