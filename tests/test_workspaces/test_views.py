from fyle_qbo_api.tests import settings
import pytest
import json
from django.urls import reverse
from tests.helper import dict_compare_keys
from apps.workspaces.models import FyleCredential, WorkspaceSchedule
from .fixtures import data

def test_get_workspace_by_id(api_client, test_connection):

    url = reverse(
        'workspace-by-id', kwargs={
            'workspace_id': 3
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    print(response)

    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'

def test_post_of_workspace(api_client, test_connection):

    url = reverse(
        'workspace'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'


def test_get_configuration_detail(api_client, test_connection):

    url = reverse(
        'workspace-general-settings', kwargs={
            'workspace_id': 4
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert dict_compare_keys(response, data['general_settings']) == [], 'configuration api returns a diff in keys'

def test_post_workspace_configurations(api_client, test_connection):
    url = reverse(
        'workspace-general-settings', kwargs={
            'workspace_id': 4
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
            'workspace_id': 4
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    response = json.loads(response.content)
    print(response)

    assert response['message'] == 'Workspace schedule does not exist in workspace'

    WorkspaceSchedule.objects.get_or_create(
        workspace_id=5
    )

    response = api_client.get(url)
    response = json.loads(response.content)

    assert response == {'enabled': False,'id': 1,'interval_hours': None,'schedule': None,'start_datetime': None,'workspace': 8}

def test_ready_view(api_client, test_connection):
    url = reverse('ready')

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    response = json.loads(response.content)

    assert response['message'] == 'Ready'


def test_delete_fyle_credentials_view(api_client, test_connection):
    url = reverse(
        'delete-fyle-credentials', kwargs={
            'workspace_id': 4
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.delete(url)
    response = json.loads(response.content)

    assert response['message'] == 'Fyle credentials deleted'


def test_get_fyle_credentials_view(api_client, test_connection):
    url = reverse(
        'get-fyle-credentials', kwargs={
            'workspace_id': 4
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    response = json.loads(response.content)

    assert response['refresh_token'] == settings.FYLE_REFRESH_TOKEN

    fyle_credentials = FyleCredential.objects.get(workspace_id=5)
    fyle_credentials.delete()

    response = api_client.get(url)

    response = json.loads(response.content)
    assert response['message'] == 'Fyle Credentials not found in this workspace'


def test_get_qbo_credentials_view(api_client, test_connection):
    url = reverse(
        'get-qbo-credentials', kwargs={
            'workspace_id': 4
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    response = json.loads(response.content)

    #Todo add a check with settings.realm_id 
    assert response['realm_id'] == '4620816365009870170'
    
# def test_delete_qbo_credentials_view(api_client, test_connection):
#     url = reverse(
#         'delete-qbo-credentials', kwargs={
#             'workspace_id': 4
#         }
#     )

#     api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

#     response = api_client.delete(url)
#     response = json.loads(response.content)

#     assert response['message'] == 'QBO credentials deleted'
