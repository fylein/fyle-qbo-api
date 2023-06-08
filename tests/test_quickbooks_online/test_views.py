from os import access
from django.urls import reverse
import pytest
import json
from unittest import mock
from apps.tasks.models import TaskLog
from apps.workspaces.models import QBOCredential
from apps.fyle.models import Reimbursement, ExpenseGroup
from .fixtures import data
from qbosdk.exceptions import WrongParamsError, InvalidTokenError
from fyle_accounting_mappings.models import DestinationAttribute



def test_destination_attributes_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = reverse('destination-attributes', 
        kwargs={
                'workspace_id': 3
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url,{
        'attribute_types':'ACCOUNT',
        'display_name':'Account'
    })
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 63

def test_searched_destination_attributes_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = reverse('searching-destination-attributes', 
        kwargs={
                'workspace_id': 3
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url,{
        'attribute_type':'ACCOUNT',
        'display_name':'Account'
    })
    assert response.status_code == 200
    response = json.loads(response.content)
    assert len(response) == 30


def test_qbo_attributes_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = reverse('qbo-attributes', 
        kwargs={
                'workspace_id': 3
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url,{
        'attribute_types':'CUSTOMER'
    })
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 1


def test_get_company_preference(mocker, api_client, test_connection, db):
    mocker.patch(
        'qbosdk.apis.Preferences.get',
        return_value=data['company_info']
    )
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/preferences/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response['Id'] == '1'


def test_get_company_preference_exceptions(api_client, test_connection, db):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/preferences/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.get_company_info') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='wrong params', response='invalid_params')
        response = api_client.get(url)
        assert response.status_code == 400

        mock_call.side_effect = InvalidTokenError(msg='Invalid token, try to refresh it', response='Invalid token, try to refresh it')
        response = api_client.get(url)
        assert response.status_code == 400

        mock_call.side_effect = QBOCredential.DoesNotExist()
        response = api_client.get(url)
        assert response.status_code == 400

        response = json.loads(response.content)
        assert response['message'] == 'QBO credentials not found in workspace'


def test_vendor_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_vendors',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/vendors/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 10

    vendor = DestinationAttribute.objects.filter(
            attribute_type='VENDOR', active=True, workspace_id=3).first()
    vendor.active = False
    vendor.save()

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 10


def test_employee_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_employees',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/employees/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 2

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.get_active_qbo_credentials(3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_post_sync_dimensions(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/sync_dimensions/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    
    assert response.status_code == 200

    with mock.patch('apps.workspaces.models.Workspace.objects.get') as mock_call:
        mock_call.side_effect = Exception()

        response = api_client.post(url)
        assert response.status_code == 400

        mock_call.side_effect = QBOCredential.DoesNotExist()

        response = api_client.post(url)
        assert response.status_code == 400


def test_post_refresh_dimensions(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/refresh_dimensions/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    
    assert response.status_code == 200

    with mock.patch('apps.workspaces.models.Workspace.objects.get') as mock_call:
        mock_call.side_effect = Exception()

        response = api_client.post(url)
        assert response.status_code == 400
         
    qbo_credential = QBOCredential.get_active_qbo_credentials(3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'
    