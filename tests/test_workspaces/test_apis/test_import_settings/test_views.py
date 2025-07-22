import json

from django.urls import reverse

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from fyle_integrations_imports.models import ImportLog
from tests.helper import dict_compare_keys
from tests.test_workspaces.test_apis.test_import_settings.fixtures import data


def test_import_settings(mocker, api_client, test_connection):
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.get_by_id', return_value={'options': ['samp'],"is_mandatory": False, 'updated_at': '2020-06-11T13:14:55.201598+00:00'})
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.post', return_value=None)
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.sync', return_value=None)
    workspace = Workspace.objects.get(id=3)
    workspace.onboarding_state = 'IMPORT_SETTINGS'
    workspace.save()

    url = '/api/v2/workspaces/3/import_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.put(url, data=data['import_settings'], format='json')

    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['response']) == [], 'workspaces api returns a diff in the keys'

    response = api_client.put(url, data=data['import_settings_without_mapping'], format='json')
    assert response.status_code == 200

    invalid_workspace_general_settings = data['import_settings']
    invalid_workspace_general_settings['workspace_general_settings'] = {}
    response = api_client.put(url, data=invalid_workspace_general_settings, format='json')
    assert response.status_code == 400

    response = json.loads(response.content)
    assert response['non_field_errors'] == ['Workspace general settings are required']

    response = api_client.put(url, data=data['invalid_general_mappings'], format='json')
    assert response.status_code == 400

    response = api_client.put(url, data=data['invalid_mapping_settings'], format='json')
    assert response.status_code == 400

    # Test with Import Fields put request with ACCOUNT
    add_import_code_fields_payload = data['import_settings_with_account']
    add_import_code_fields_payload['workspace_general_settings']['import_code_fields'] = []
    response = api_client.put(
        url,
        data=add_import_code_fields_payload,
        format='json'
    )

    assert response.status_code == 200
    # Test with categories import without code and then adding code
    import_log = ImportLog.objects.create(
        workspace_id=3,
        attribute_type='CATEGORY',
        status='COMPLETE'
    )

    add_import_code_fields_payload['workspace_general_settings']['import_code_fields'] = ['ACCOUNT']
    response = api_client.put(
        url,
        data=add_import_code_fields_payload,
        format='json'
    )
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['non_field_errors'] == ["Cannot change the code fields once they are imported"]

    # Test with categories import with code and then removing code
    import_log.delete()
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workspace_general_settings.import_code_fields = ['ACCOUNT']
    workspace_general_settings.save()

    add_import_code_fields_payload['workspace_general_settings']['import_code_fields'] = []
    response = api_client.put(
        url,
        data=add_import_code_fields_payload,
        format='json'
    )
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['non_field_errors'] == ["Cannot change the code fields once they are imported"]


def test_import_code_field_view(db, mocker, api_client, test_connection):
    """
    Test ImportCodeFieldView
    """
    workspace_id = 1
    url = reverse('import-code-fields-config', kwargs={'workspace_id': workspace_id})
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    category_log, _ = ImportLog.objects.update_or_create(
        attribute_type='CATEGORY',
        workspace_id=workspace_id,
        status='COMPLETE'
    )

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data == {
        'ACCOUNT': False
    }

    category_log.delete()
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data == {
        'ACCOUNT': True
    }
