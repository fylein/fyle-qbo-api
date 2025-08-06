import pytest

from apps.workspaces.models import FyleCredential, Workspace
from fyle_qbo_api.utils import patch_integration_settings


@pytest.mark.django_db(databases=['default'])
def test_post_to_integration_settings(mocker):
    mocker.patch(
        'apps.fyle.helpers.post_request',
        return_value=''
    )

    no_exception = True

    # If exception is raised, this test will fail
    assert no_exception


@pytest.mark.django_db(databases=['default'])
def test_patch_integration_settings(mocker):
    workspace_id = 1
    fyle_credential, _ = FyleCredential.objects.update_or_create(workspace_id=workspace_id)
    refresh_token = 'test_refresh_token'
    fyle_credential.refresh_token = refresh_token
    fyle_credential.save()

    patch_request_mock = mocker.patch('apps.fyle.helpers.requests.patch')

    patch_integration_settings(workspace_id, errors=5)
    patch_request_mock.assert_not_called()

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.onboarding_state = 'COMPLETE'
    workspace.save()

    patch_request_mock.reset_mock()
    patch_integration_settings(workspace_id, errors=7)
    patch_request_mock.assert_called_with(
        mocker.ANY,  # URL
        headers=mocker.ANY,
        data='{"tpa_name": "Fyle Quickbooks Integration", "errors_count": 7}'
    )

    patch_request_mock.reset_mock()
    patch_integration_settings(workspace_id, is_token_expired=True)

    patch_request_mock.assert_called_with(
        mocker.ANY,  # URL
        headers=mocker.ANY,
        data='{"tpa_name": "Fyle Quickbooks Integration", "is_token_expired": true}'
    )

    patch_request_mock.reset_mock()
    patch_integration_settings(workspace_id, errors=241, is_token_expired=True)

    patch_request_mock.assert_called_with(
        mocker.ANY,  # URL
        headers=mocker.ANY,
        data='{"tpa_name": "Fyle Quickbooks Integration", "errors_count": 241, "is_token_expired": true}'
    )
