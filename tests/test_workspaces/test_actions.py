import json
from unittest.mock import MagicMock

import pytest

from apps.workspaces.actions import post_to_integration_settings
from fyle_qbo_api.utils import patch_integration_settings


@pytest.mark.django_db(databases=['default'])
def test_post_to_integration_settings(mocker):
    mocker.patch(
        'apps.fyle.helpers.post_request',
        return_value=''
    )

    no_exception = True
    post_to_integration_settings(1, True)

    # If exception is raised, this test will fail
    assert no_exception


@pytest.mark.django_db(databases=['default'])
def test_patch_integration_settings(mocker):

    workspace_id = 1
    mocked_patch = MagicMock()
    mocker.patch('apps.fyle.helpers.requests.patch', side_effect=mocked_patch)

    # Test patch request with only errors
    errors = 7
    patch_integration_settings(workspace_id, errors)

    expected_payload = {'errors_count': errors, 'tpa_name': 'Fyle Quickbooks Integration'}

    _, kwargs = mocked_patch.call_args
    actual_payload = json.loads(kwargs['data'])

    assert actual_payload == expected_payload

    # Test patch request with only is_token_expired
    is_token_expired = True
    patch_integration_settings(workspace_id, is_token_expired=is_token_expired)

    expected_payload = {'is_token_expired': is_token_expired, 'tpa_name': 'Fyle Quickbooks Integration'}

    _, kwargs = mocked_patch.call_args
    actual_payload = json.loads(kwargs['data'])

    assert actual_payload == expected_payload

    # Test patch request with errors_count and is_token_expired
    is_token_expired = True
    errors = 241
    patch_integration_settings(workspace_id, errors=errors, is_token_expired=is_token_expired)

    expected_payload = {
        'errors_count': errors,
        'is_token_expired': is_token_expired,
        'tpa_name': 'Fyle Quickbooks Integration'
    }

    _, kwargs = mocked_patch.call_args
    actual_payload = json.loads(kwargs['data'])

    assert actual_payload == expected_payload
