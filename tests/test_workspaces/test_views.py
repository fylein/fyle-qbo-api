from fyle_qbo_api.tests import settings
import pytest
import json
from django.urls import reverse
from tests.helper import dict_compare_keys
from apps.workspaces.models import FyleCredential, WorkspaceSchedule, WorkspaceGeneralSettings, QBOCredential
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
    workspace_id = 4
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first() 
    workspace_general_settings.map_merchant_to_vendor = True
    workspace_general_settings.save()

    url = reverse(
        'workspace-general-settings', kwargs={
            'workspace_id': workspace_id
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

    assert response['schedule'] == None

    WorkspaceSchedule.objects.get_or_create(
        workspace_id=5
    )

    response = api_client.get(url)
    response = json.loads(response.content)

    assert response == {'id': 3, 'enabled': False, 'start_datetime': None, 'interval_hours': None, 'workspace': 4, 'schedule': None, 'additional_email_options': [], 'emails_selected': None, 'error_count': None}

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
    fyle_credentials = FyleCredential.objects.get(workspace_id=4)

    assert response['refresh_token'] == fyle_credentials.refresh_token

    fyle_credentials = FyleCredential.objects.get(workspace_id=4)
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

    assert response['realm_id'] == '4620816365009870170'

    qbo_credentials = QBOCredential.objects.get(workspace=4)
    qbo_credentials.delete() 
    response = api_client.get(url)
    response = json.loads(response.content)

    assert response['message'] == 'QBO Credentials not found in this workspace'
    

def test_post_connect_fyle_view(api_client, test_connection):
    code = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiJ0cGFWVVhtd2FZWGVRIiwicmVzcG9uc2VfdHlwZSI6ImNvZGUiLCJjbHVzdGVyX2RvbWFpbiI6Imh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2giLCJvcmdfdXNlcl9pZCI6Im91NDV2ekhFWUJGUyIsImV4cCI6MTY1MjI2MzMwMH0.D6WdXnkUcKMU98VjZEMz6OH1kGtRXVj1uLGsTeIo0IQ'
    url = '/api/workspaces/5/connect_fyle/authorization_code/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(
        url,
        data={code: code}    
    )
    response = api_client.post(url)
    assert response.status_code == 500


def test_post_connect_qbo_view(api_client, test_connection):
    code = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiJ0cGFWVVhtd2FZWGVRIiwicmVzcG9uc2VfdHlwZSI6ImNvZGUiLCJjbHVzdGVyX2RvbWFpbiI6Imh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2giLCJvcmdfdXNlcl9pZCI6Im91NDV2ekhFWUJGUyIsImV4cCI6MTY1MjI2MzMwMH0.D6WdXnkUcKMU98VjZEMz6OH1kGtRXVj1uLGsTeIo0IQ'
    url = '/api/workspaces/5/connect_qbo/authorization_code/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(
        url,
        data={code: code}    
    )
    response = api_client.post(url)

    response = json.loads(response.content)
    assert response['error_description'] == 'Invalid authorization code'
