
from unittest.mock import MagicMock
from apps.exceptions import handle_view_exceptions
from fyle_qbo_api.utils import invalidate_qbo_credentials
from apps.workspaces.models import QBOCredential

def test_invalidate_qbo_credentials(mocker, db):
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id=workspace_id)

    mocked_patch = MagicMock()
    mocker.patch('fyle_qbo_api.utils.patch_integration_settings', side_effect=mocked_patch)

    # Should not fail if qbo_credentials was not found
    qbo_credentials.delete()
    invalidate_qbo_credentials(workspace_id)
    assert not mocked_patch.called

    # Should not call patch_integration_settings if qbo_credentials.is_expired is True
    qbo_credentials.is_expired = True
    qbo_credentials.save()
    invalidate_qbo_credentials(workspace_id)
    assert not mocked_patch.called

    # Should call patch_integration_settings with the correct arguments if qbo_credentials.is_expired is False
    qbo_credentials.is_expired = False
    qbo_credentials.save()

    invalidate_qbo_credentials(workspace_id)

    args, kwargs = mocked_patch.call_args
    assert args[0] == workspace_id
    assert kwargs['is_token_expired'] == True
