import json

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from tests.helper import dict_compare_keys
from tests.test_workspaces.test_apis.test_map_employee.fixtures import data


def test_map_employees(api_client, test_connection):

    workspace = Workspace.objects.get(id=3)
    workspace.onboarding_state = 'EXPORT_SETTINGS'
    workspace.save()

    workspace_general_settings_instance = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    workspace_general_settings_instance.employee_field_mapping = 'VENDOR'
    workspace_general_settings_instance.save()

    url = '/api/v2/workspaces/3/map_employees/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.put(url, data=data['map_employees'], format='json')

    assert response.status_code == 200

    response = json.loads(response.content)

    assert dict_compare_keys(response, data['response']) == [], 'workspaces api returns a diff in the keys'

    response = api_client.put(url, data=data['missing_employee_mapping'], format='json')

    assert response.status_code == 400
    response = json.loads(response.content)

    response = api_client.put(url, data=data['invalid_auto_map_employees'], format='json')

    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['non_field_errors'][0] == 'auto_map_employees can have only EMAIL / NAME / EMPLOYEE_CODE'
