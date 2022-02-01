import pytest
import json
from django.urls import reverse
from tests.helper import dict_compare_keys
from apps.workspaces.models import WorkspaceSchedule
from .fixtures import data

@pytest.mark.django_db(databases=['default'])
def test_get_workspace_by_id(api_client, test_connection):

    url = reverse(
        'workspace-by-id', kwargs={
            'workspace_id': 9
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)

    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'

@pytest.mark.django_db(databases=['default'])
def test_post_of_workspace(api_client, test_connection):

    url = reverse(
        'workspace'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    
    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'


@pytest.mark.django_db(databases=['default'])
def test_get_configuration_detail(api_client, test_connection):

    url = reverse(
        'workspace-general-settings', kwargs={
            'workspace_id': 9
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert dict_compare_keys(response, data['general_settings']) == [], 'configuration api returns a diff in keys'

@pytest.mark.django_db(databases=['default'])
def test_post_workspace_configurations(api_client, test_connection):
    url = reverse(
        'workspace-general-settings', kwargs={
            'workspace_id': 8
        }
    )
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(
        url,
        data=data['workspace_general_settings_payload'],
        format='json'
    )

    assert response.status_code==200



def test_get_workspace_schedule(api_client, test_connection):
    url = reverse(
        'workspace-schedule', kwargs={
            'workspace_id': 8
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    response = json.loads(response.content)

    assert response['message'] == 'Workspace schedule does not exist in workspace'

    WorkspaceSchedule.objects.get_or_create(
        workspace_id=8
    )

    response = api_client.get(url)
    response = json.loads(response.content)

    assert response == {'enabled': False,'id': 1,'interval_hours': None,'schedule': None,'start_datetime': None,'workspace': 8}
