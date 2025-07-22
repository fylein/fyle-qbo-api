import json
from datetime import datetime, timedelta
from unittest import mock

from django.db.models import Q
from django.urls import reverse
from qbosdk import exceptions as qbo_exc

from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.models import QBOSyncTimestamp
from apps.tasks.models import TaskLog
from apps.workspaces.actions import export_to_qbo
from apps.workspaces.models import LastExportDetail, QBOCredential, Workspace, WorkspaceGeneralSettings
from fyle_qbo_api.tests import settings
from tests.helper import dict_compare_keys
from tests.test_workspaces.fixtures import data


def test_get_qbo_token_health(mocker, api_client, test_connection):
    workspace_id = 1
    mocker.patch("apps.quickbooks_online.utils.QBOConnector.__init__", return_value=None)
    mocker.patch("apps.quickbooks_online.utils.QBOConnector.get_company_preference", return_value={'CompanyName': 'Test Company'})

    access_token = test_connection.access_token
    url = "/api/workspaces/{}/token_health/".format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    QBOCredential.objects.filter(workspace=workspace_id).delete()

    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == "Quickbooks Online credentials not found"

    QBOCredential.objects.create(workspace_id=workspace_id, refresh_token="some_token", is_expired=True)
    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == "Quickbooks Online connection expired"

    QBOCredential.objects.filter(workspace=workspace_id).delete()
    QBOCredential.objects.create(workspace_id=workspace_id, refresh_token=None, is_expired=False)
    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == "Quickbooks Online disconnected"

    QBOCredential.objects.filter(workspace=workspace_id).delete()
    QBOCredential.objects.create(workspace_id=workspace_id, refresh_token="valid_refresh_token", is_expired=False)
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['message'] == "Quickbooks Online connection is active"

    mocker.patch("apps.quickbooks_online.utils.QBOConnector.get_company_preference", side_effect=qbo_exc.InvalidTokenError("Token expired"))
    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == "Quickbooks Online connection expired"

    mocker.patch("apps.quickbooks_online.utils.QBOConnector.get_company_preference", side_effect=qbo_exc.WrongParamsError("Wrong parameters"))
    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == "Quickbooks Online connection expired"


def test_get_workspace(api_client, test_connection):

    url = reverse('workspace')

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)

    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'


def test_patch_of_workspace(api_client, test_connection):

    url = reverse('workspace-by-id', kwargs={'workspace_id': 3})

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.patch(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'


def test_post_of_workspace(mocker, api_client, test_connection):
    mocker.patch('apps.workspaces.actions.get_fyle_admin', return_value={'data': {'org': {'name': 'Test Trip', 'id': 'orZu2yrz7zdy', 'currency': 'USD'}}})
    url = reverse('workspace')

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
    QBOSyncTimestamp.objects.filter(workspace_id=1).delete()
    mocker.patch('apps.workspaces.actions.get_fyle_admin', return_value={'data': {'org': {'name': 'Test Trip', 'id': 'orZu2y7zdy', 'currency': 'USD'}}})
    url = reverse('workspace')

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(url)
    assert response.status_code == 200


def test_get_configuration_detail(db, api_client, test_connection):
    workspace_id = 4

    url = '/api/workspaces/4/settings/general/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['general_settings']) == [], 'configuration api returns a diff in keys'

    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    workspace_general_settings.delete()

    response = api_client.get(url)
    assert response.status_code == 404


def test_ready_view(api_client, test_connection):
    url = reverse('ready')

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    response = json.loads(response.content)

    assert response['message'] == 'Ready'


def test_post_connect_qbo_view(mocker, api_client, test_connection):
    mocker.patch('apps.workspaces.views.generate_qbo_refresh_token', return_value='asdfghjk')
    mocker.patch('qbosdk.apis.CompanyInfo.get', return_value=data['company_info'])
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.get_company_preference', return_value={'CurrencyPrefs': {'HomeCurrency': {'value': 'USD'}}})
    mocked_patch = mock.MagicMock()
    mocker.patch('apps.workspaces.actions.patch_integration_settings', side_effect=mocked_patch)

    workspace_id = 5

    code = 'sdfg'
    url = f'/api/workspaces/{workspace_id}/connect_qbo/authorization_code/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    qbo_credentials = QBOCredential.objects.filter(workspace=workspace_id).first()
    qbo_credentials.delete()

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.onboarding_state = 'CONNECTION'
    workspace.save()

    response = api_client.post(url, data={'code': code, 'realm_id': '123146326950399'})

    assert response.status_code == 200

    args, kwargs = mocked_patch.call_args
    assert args[0] == workspace_id
    assert kwargs['is_token_expired'] == False

    response = api_client.post(url, data={'code': code, 'realm_id': '12248888999009'})
    assert response.status_code == 400


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

        response = api_client.post(url, data={'code': code})
        assert response.status_code == 401

        mock_call.side_effect = qbo_exc.NotFoundClientError(msg='Fyle Application not found', response='Fyle Application not found')

        response = api_client.post(url, data={'code': code})
        assert response.status_code == 401

        mock_call.side_effect = qbo_exc.WrongParamsError(msg='Some of the parameters are wrong', response='Some of the parameters are wrong')

        response = api_client.post(url, data={'code': code})
        assert response.status_code == 401

        mock_call.side_effect = qbo_exc.InternalServerError(msg='Wrong/Expired Authorization code', response='Wrong/Expired Authorization code')

        response = api_client.post(url, data={'code': code})
        assert response.status_code == 401


@mock.patch('apps.workspaces.views.connection')
def test_prepare_e2e_test_view(mock_db, mocker, api_client, test_connection):
    url = reverse('setup-e2e-test', kwargs={'workspace_id': 3})

    api_client.credentials(HTTP_X_Internal_API_Client_ID='dummy_id')
    response = api_client.post(url)
    assert response.status_code == 403

    mocker.patch('cryptography.fernet.Fernet.decrypt', return_value=settings.E2E_TESTS_CLIENT_SECRET.encode('utf-8'))

    mocker.patch('apps.quickbooks_online.utils.QBOConnector.sync_dimensions', return_value=None)
    mocker.patch('fyle_integrations_platform_connector.fyle_integrations_platform_connector.PlatformConnector.import_fyle_dimensions', return_value=[])
    mocker.patch('apps.workspaces.models.QBOCredential.objects.create', return_value=None)

    api_client.credentials(HTTP_X_Internal_API_Client_ID='dummy_id')
    response = api_client.post(url)
    assert response.status_code == 400

    mocker.patch('apps.quickbooks_online.utils.QBOConnector.get_company_preference', return_value=None)
    healthy_token = QBOCredential.objects.get(workspace_id=3)
    healthy_token.is_expired = False
    healthy_token.save()

    api_client.credentials(HTTP_X_Internal_API_Client_ID='gAAAAABi8oXHBll3lEUPGpMDXnZDhVgSl_LMOkIF0ilfmSCL3wFxZnoTIbpdzwPoOFzS0vFO4qaX51JtAqCG2RBHZaf1e98hug==')
    response = api_client.post(url)
    assert response.status_code == 200

    url = reverse('setup-e2e-test', kwargs={'workspace_id': 6})
    api_client.credentials(HTTP_X_Internal_API_Client_ID='gAAAAABi8oWVoonxF0K_g2TQnFdlpOJvGsBYa9rPtwfgM-puStki_qYbi0PdipWHqIBIMip94MDoaTP4MXOfERDeEGrbARCxPw==')
    response = api_client.post(url)
    assert response.status_code == 400


def test_export_to_qbo(mocker, api_client, test_connection):
    mocker.patch('apps.workspaces.views.export_to_qbo', return_value=None)

    workspace_id = 3
    url = '/api/workspaces/{}/exports/trigger/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(url)
    assert response.status_code == 200

    ExpenseGroup.objects.filter(workspace_id=workspace_id).update(exported_at=None)
    expense_group_ids = ExpenseGroup.objects.filter(workspace_id=workspace_id).values_list('id', flat=True)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    assert qbo_credentials is not None
    assert len(expense_group_ids) != 0
    export_to_qbo(workspace_id, expense_group_ids=expense_group_ids)
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    last_exported_at = last_export_detail.last_exported_at
    assert last_exported_at.replace(tzinfo=None) > (datetime.now() - timedelta(minutes=1)).replace(tzinfo=None)

    qbo_credentials.is_expired = True
    qbo_credentials.save()

    export_to_qbo(workspace_id, expense_group_ids=expense_group_ids)
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    assert last_export_detail.last_exported_at == last_exported_at


def test_last_export_detail_view(db, api_client, test_connection):
    workspace_id = 3
    url = '/api/workspaces/{}/export_detail/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200


def test_last_export_detail_2(mocker, api_client, test_connection):
    workspace_id = 3

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(
        reimbursable_expenses_object='BILL',
        corporate_credit_card_expenses_object='BILL'
    )

    url = "/api/workspaces/{}/export_detail/?start_date=2025-05-01".format(workspace_id)

    api_client.credentials(
        HTTP_AUTHORIZATION="Bearer {}".format(test_connection.access_token)
    )

    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    last_export_detail.last_exported_at = datetime.now()
    last_export_detail.total_expense_groups_count = 1
    last_export_detail.save()

    task_log = TaskLog.objects.filter(~Q(type__in=['CREATING_BILL_PAYMENT', 'FETCHING_EXPENSES']), workspace_id=workspace_id, status='COMPLETE').first()
    task_log.updated_at = datetime.now()
    task_log.save()

    failed_count = TaskLog.objects.filter(workspace_id=workspace_id, status__in=['FAILED', 'FATAL']).count()

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response['repurposed_successful_count'] == 1
    assert response['repurposed_failed_count'] == failed_count
    assert response['repurposed_last_exported_at'] is not None


def test_workspace_admin_view(mocker, db, api_client, test_connection):

    workspace_id = 3
    url = '/api/workspaces/{}/admins/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200
