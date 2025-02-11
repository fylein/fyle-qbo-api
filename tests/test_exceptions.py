
from unittest.mock import MagicMock
from apps.exceptions import handle_view_exceptions, invalidate_token
from apps.workspaces.models import QBOCredential
from qbosdk.exceptions import InvalidTokenError, WrongParamsError


def test_handle_view_exceptions(mocker):
    workspace_id = 123

    mocked_invalidate_token = MagicMock()
    mocker.patch('apps.exceptions.invalidate_token', side_effect=mocked_invalidate_token)

    @handle_view_exceptions()
    def func(*args, **kwargs):
        raise WrongParamsError('Invalid Token')

    func(workspace_id=workspace_id)

    args, _ = mocked_invalidate_token.call_args
    assert args[0] == workspace_id

    @handle_view_exceptions()
    def func(*args, **kwargs):
        raise InvalidTokenError('Invalid Token')

    func(workspace_id=workspace_id)

    args, _ = mocked_invalidate_token.call_args
    assert args[0] == workspace_id


def test_invalidate_token(mocker, db):
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id=workspace_id)

    mocked_patch = MagicMock()
    mocker.patch('apps.exceptions.patch_integration_settings', side_effect=mocked_patch)

    # Should not fail if qbo_credentials was not found
    qbo_credentials.delete()
    invalidate_token(workspace_id)
    assert not mocked_patch.called

    # Should not call patch_integration_settings if qbo_credentials.is_expired is True
    qbo_credentials.is_expired = True
    qbo_credentials.save()
    invalidate_token(workspace_id)
    assert not mocked_patch.called

    # Should call patch_integration_settings with the correct arguments if qbo_credentials.is_expired is False
    qbo_credentials.is_expired = False
    qbo_credentials.save()

    invalidate_token(workspace_id)

    args, kwargs = mocked_patch.call_args
    assert args[0] == workspace_id
    assert kwargs['is_token_expired'] == True
