from fyle_qbo_api.tests import settings
import pytest
import json
from django.urls import reverse
from unittest import mock
from tests.helper import dict_compare_keys
from fyle.platform import exceptions as fyle_exc
from qbosdk import exceptions as qbo_exc
from apps.workspaces.models import *
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

    with mock.patch('apps.workspaces.models.Workspace.objects.get') as mock_call:
        mock_call.side_effect = Workspace.DoesNotExist()

        response = api_client.get(url)
        assert response.status_code == 400


def test_get_workspace(api_client, test_connection):

    url = reverse(
        'workspace'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)

    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'


def test_patch_of_workspace(api_client, test_connection):

    url = reverse(
        'workspace-by-id', kwargs={
            'workspace_id': 3
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.patch(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'


def test_post_of_workspace(mocker, api_client, test_connection):
    mocker.patch(
        'apps.workspaces.views.get_fyle_admin',
        return_value={'data': {'org': {'name': 'Test Trip', 'id': 'orZu2yrz7zdy', 'currency': 'USD'}}}
    )
    url = reverse(
        'workspace'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'
    
    workspace = Workspace.objects.filter(fyle_org_id='or79Cob97KSh').first()
    workspace.fyle_org_id = 'asdfghj'
    workspace.save()

    response = api_client.post(url)
    assert response.status_code == 200


def test_post_of_new_workspace(mocker, api_client, test_connection):
    mocker.patch(
        'apps.workspaces.views.get_fyle_admin',
        return_value={'data': {'org': {'name': 'Test Trip', 'id': 'orZu2y7zdy', 'currency': 'USD'}}}
    )
    url = reverse(
        'workspace'
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)
    assert response.status_code == 200


def test_get_configuration_detail(api_client, test_connection):
    workspace_id = 4

    url = reverse(
        'workspace-general-settings', kwargs={
            'workspace_id': workspace_id
        }
    )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['general_settings']) == [], 'configuration api returns a diff in keys'

    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first() 
    workspace_general_settings.delete()

    response = api_client.get(url)
    assert response.status_code == 400


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

    response = api_client.patch(
        url,
        data=data['workspace_general_settings_payload'],
        format='json'
    )
    assert response.status_code==200

    updated_data = data['workspace_general_settings_payload']
    updated_data['je_single_credit_line'] = True
    updated_data['corporate_credit_card_expenses_object'] = 'JOURNAL ENTRY'

    response = api_client.post(
        url,
        data=updated_data,
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

    qbo_credentials = QBOCredential.get_active_qbo_credentials(4)
    qbo_credentials.delete()
    response = api_client.get(url)
    response = json.loads(response.content)

    assert response['message'] == 'QBO Credentials not found in this workspace'
    

def test_post_connect_fyle_view(mocker, api_client, test_connection):
    mocker.patch(
        'fyle_rest_auth.utils.AuthUtils.generate_fyle_refresh_token',
        return_value={'refresh_token': 'asdfghjk', 'access_token': 'qwertyuio'}
    )
    mocker.patch(
        'apps.workspaces.views.get_fyle_admin',
        return_value={'data': {'org': {'name': 'Test Trip', 'id': 'orZu2yrz7zdy', 'currency': 'USD'}}}
    )
    mocker.patch(
        'apps.workspaces.views.get_cluster_domain',
        return_value='https://staging.fyle.tech'
    )
    code = 'asd'
    url = '/api/workspaces/5/connect_fyle/authorization_code/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(
        url,
        data={'code': code}    
    )
    response = api_client.post(url)
    assert response.status_code == 200


def test_connect_fyle_view_exceptions(api_client, test_connection):
    workspace_id = 5
    
    code = 'qwertyu'
    url = '/api/workspaces/{}/connect_fyle/authorization_code/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    with mock.patch('fyle_rest_auth.utils.AuthUtils.generate_fyle_refresh_token') as mock_call:
        mock_call.side_effect = fyle_exc.UnauthorizedClientError(msg='Invalid Authorization Code', response='Invalid Authorization Code')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 403

        mock_call.side_effect = fyle_exc.NotFoundClientError(msg='Fyle Application not found', response='Fyle Application not found')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 404

        mock_call.side_effect = fyle_exc.WrongParamsError(msg='Some of the parameters are wrong', response='Some of the parameters are wrong')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 400

        mock_call.side_effect = fyle_exc.InternalServerError(msg='Wrong/Expired Authorization code', response='Wrong/Expired Authorization code')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 401


def test_post_connect_qbo_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.workspaces.views.generate_qbo_refresh_token',
        return_value='asdfghjk'
    )
    mocker.patch(
        'qbosdk.apis.CompanyInfo.get',
        return_value=data['company_info']
    )
    code = 'sdfg'
    url = '/api/workspaces/5/connect_qbo/authorization_code/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    qbo_credentials = QBOCredential.objects.filter(workspace=5).first()
    qbo_credentials.delete()

    workspace = Workspace.objects.get(id=5)
    workspace.onboarding_state = 'CONNECTION'
    workspace.save()

    response = api_client.post(
        url,
        data={
            'code': code,
            'realm_id': '123146326950399',
        }    
    )
    response = api_client.post(url)
    assert response.status_code == 200


def test_patch_connect_qbo_view(mocker, api_client, test_connection):

    url = '/api/workspaces/5/connect_qbo/authorization_code/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.patch(url)
    response = json.loads(response.content)

    assert response['message'] == 'QBO Refresh Token deleted'


def test_connect_qbo_view_exceptions(api_client, test_connection):
    workspace_id = 1
    
    code = 'qwertyu'
    url = '/api/workspaces/{}/connect_qbo/authorization_code/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    with mock.patch('apps.workspaces.views.generate_qbo_refresh_token') as mock_call:
        mock_call.side_effect = qbo_exc.UnauthorizedClientError(msg='Invalid Authorization Code', response='Invalid Authorization Code')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 401

        mock_call.side_effect = qbo_exc.NotFoundClientError(msg='Fyle Application not found', response='Fyle Application not found')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 404

        mock_call.side_effect = qbo_exc.WrongParamsError(msg='Some of the parameters are wrong', response='Some of the parameters are wrong')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 500

        mock_call.side_effect = qbo_exc.InternalServerError(msg='Wrong/Expired Authorization code', response='Wrong/Expired Authorization code')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 401


@mock.patch('apps.workspaces.views.connection')
def test_prepare_e2e_test_view(mock_db, mocker, api_client, test_connection):
    url = reverse(
        'setup-e2e-test', kwargs={
            'workspace_id': 3
        }
    )

    api_client.credentials(HTTP_X_E2E_Tests_Client_ID='dummy_id')
    response = api_client.post(url)
    assert response.status_code == 403

    mocker.patch(
        'cryptography.fernet.Fernet.decrypt',
        return_value=settings.E2E_TESTS_CLIENT_SECRET.encode('utf-8')
    )
   
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_dimensions',
        return_value=None
    )
    mocker.patch(
        'fyle_integrations_platform_connector.fyle_integrations_platform_connector.PlatformConnector.import_fyle_dimensions',
        return_value=[]
    )
    mocker.patch(
        'apps.workspaces.models.QBOCredential.objects.create',
        return_value=None
    )

    api_client.credentials(HTTP_X_E2E_Tests_Client_ID='dummy_id')
    response = api_client.post(url)
    assert response.status_code == 400

    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.get_company_preference',
        return_value=None
    )
    healthy_token = QBOCredential.objects.get(workspace_id=3)
    healthy_token.is_expired = False
    healthy_token.save()

    api_client.credentials(HTTP_X_E2E_Tests_Client_ID='gAAAAABi8oXHBll3lEUPGpMDXnZDhVgSl_LMOkIF0ilfmSCL3wFxZnoTIbpdzwPoOFzS0vFO4qaX51JtAqCG2RBHZaf1e98hug==')
    response = api_client.post(url)
    assert response.status_code == 200

    url = reverse(
        'setup-e2e-test', kwargs={
            'workspace_id': 6
        }
    )
    api_client.credentials(HTTP_X_E2E_Tests_Client_ID='gAAAAABi8oWVoonxF0K_g2TQnFdlpOJvGsBYa9rPtwfgM-puStki_qYbi0PdipWHqIBIMip94MDoaTP4MXOfERDeEGrbARCxPw==')
    response = api_client.post(url)
    assert response.status_code == 500


def test_schedule_sync_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.workspaces.views.run_sync_schedule',
        return_value=None
    )

    workspace_id = 3
    url = '/api/workspaces/{}/schedule/trigger/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(url)
    assert response.status_code == 200


def test_schedule_view(mocker, db, api_client, test_connection):
    mocker.patch(
        'apps.workspaces.views.run_sync_schedule',
        return_value=None
    )

    workspace_id = 3
    url = '/api/workspaces/{}/schedule/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = api_client.post(
        url,
        data={
            'schedule_enabled': True,
            'hours': 1
        },
        format='json'
    )
    assert response.status_code == 200

    workspace_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id).first() 
    workspace_schedule.delete()

    response = api_client.get(url)
    assert response.status_code == 400


def test_export_to_qbo(mocker, api_client, test_connection):
    mocker.patch(
        'apps.workspaces.views.export_to_qbo',
        return_value=None
    )

    workspace_id = 3
    url = '/api/workspaces/{}/exports/trigger/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(url)
    assert response.status_code == 200


def test_last_export_detail_view(mocker, db, api_client, test_connection):

    workspace_id = 3
    url = '/api/workspaces/{}/export_detail/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    last_export_detail = LastExportDetail.objects.filter(workspace_id=workspace_id).first()
    last_export_detail.total_expense_groups_count = 0
    last_export_detail.save()

    response = api_client.get(url)
    assert response.status_code == 400


def test_workspace_admin_view(mocker, db, api_client, test_connection):

    workspace_id = 3
    url = '/api/workspaces/{}/admins/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200