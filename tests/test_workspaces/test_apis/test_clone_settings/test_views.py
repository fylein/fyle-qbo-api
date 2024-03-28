
import json
from apps.workspaces.models import Workspace
from tests.helper import dict_compare_keys
from .fixtures import data
from tests.test_fyle_integrations_imports.test_modules.fixtures import expense_custom_field_data


def assert_4xx_cases(api_client, url, payload):
    response = api_client.put(
        url,
        data=payload,
        format='json'
    )

    assert response.status_code == 400


def test_clone_settings(mocker, api_client, test_connection):
    workspace = Workspace.objects.get(id=1)
    workspace.name_in_journal_entry = 'MERCHANT'
    workspace.onboarding_state = 'COMPLETE'
    workspace.save()

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.expense_fields.list_all',
        return_value=expense_custom_field_data['create_new_auto_create_expense_custom_fields_expense_attributes_0']
    )

    url = '/api/v2/workspaces/1/clone_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.put(
        url,
        data=data['clone_settings'],
        format='json'
    )

    assert response.status_code == 200
    response = json.loads(response.content)
    assert dict_compare_keys(response, data['clone_settings_response']) == [], \
        'clone settings api returns a diff in the keys'

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)
    assert dict_compare_keys(response, data['clone_settings_response']) == [], \
        'clone settings api returns a diff in the keys'

    response = api_client.put(
        url,
        data=data['clone_settings_missing_values'],
        format='json'
    )

    assert response.status_code == 400


def test_4xx_export_settings(api_client, test_connection):
    url = '/api/v2/workspaces/1/clone_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    assert_4xx_cases(api_client, url, {})


def test_4xx_import_settings(api_client, test_connection):
    url = '/api/v2/workspaces/1/clone_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    assert_4xx_cases(api_client, url, {
        'export_settings': data['clone_settings']['export_settings']
    })


def test_4xx_advanced_settings(api_client, test_connection):
    url = '/api/v2/workspaces/1/clone_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    assert_4xx_cases(api_client, url, {
        'export_settings': data['clone_settings']['export_settings'],
        'import_settings': data['clone_settings']['import_settings']
    })


def test_clone_settings_exists(api_client, test_connection):
    workspace = Workspace.objects.get(id=1)
    workspace.onboarding_state = 'COMPLETE'
    workspace.save()

    url = '/api/user/clone_settings/exists/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(
        url,
        data=data['clone_settings_exists'],
        format='json'
    )

    assert response.status_code == 200
    response = json.loads(response.content)
    assert dict_compare_keys(response, data['clone_settings_exists']) == [], \
        'clone settings api returns a diff in the keys'

    Workspace.objects.update(onboarding_state='EXPORT_SETTINGS')

    response = api_client.get(
        url,
        data=data['clone_settings_exists'],
        format='json'
    )

    assert response.status_code == 200
    response = json.loads(response.content)
    assert dict_compare_keys(response, data['clone_settings_not_exists']) == [], \
        'clone settings api returns a diff in the keys'
