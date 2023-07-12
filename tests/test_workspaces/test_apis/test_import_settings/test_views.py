import json
from datetime import timedelta

from django_q.models import Schedule

from apps.workspaces.models import Workspace
from tests.helper import dict_compare_keys

from .fixtures import data


def test_import_settings(mocker, api_client, test_connection):
    mocker.patch(
        'fyle_integrations_platform_connector.apis.ExpenseCustomFields.get_by_id',
        return_value={'options': ['samp'], 'updated_at': '2020-06-11T13:14:55.201598+00:00'}
    )
    mocker.patch(
        'fyle_integrations_platform_connector.apis.ExpenseCustomFields.post',
        return_value=None
    )
    mocker.patch(
        'fyle_integrations_platform_connector.apis.ExpenseCustomFields.sync',
        return_value=None
    )
    workspace = Workspace.objects.get(id=3)
    workspace.onboarding_state = 'IMPORT_SETTINGS'
    workspace.save()

    url = '/api/v2/workspaces/3/import_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.put(
        url,
        data=data['import_settings'],
        format='json'
    )

    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['response']) == [], 'workspaces api returns a diff in the keys'

    response = api_client.put(
        url,
        data=data['import_settings_without_mapping'],
        format='json'
    )
    assert response.status_code == 200

    invalid_workspace_general_settings = data['import_settings']
    invalid_workspace_general_settings['workspace_general_settings'] = {}
    response = api_client.put(
        url,
        data=invalid_workspace_general_settings,
        format='json'
    )
    assert response.status_code == 400

    response = json.loads(response.content)
    assert response['non_field_errors'] == ['Workspace general settings are required']

    response = api_client.put(
        url,
        data=data['invalid_general_mappings'],
        format='json'
    )
    assert response.status_code == 400

    response = api_client.put(
        url,
        data=data['invalid_mapping_settings'],
        format='json'
    )
    assert response.status_code == 400
