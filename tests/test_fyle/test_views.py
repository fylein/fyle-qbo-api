import pytest
from apps.workspaces.models import FyleCredential, Workspace
from unittest import mock
import json
from fyle_accounting_mappings.models import DestinationAttribute
from django.urls import reverse
from .fixtures import data
from tests.helper import dict_compare_keys
from apps.tasks.models import TaskLog


def test_expense_group_view(api_client, test_connection):
    access_token = test_connection.access_token

    url = reverse('expense-groups', 
            kwargs={
                'workspace_id': 3,
                }
            )
    
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url, {
        'expense_group_ids': '1,2'
    })
    assert response.status_code==200

    response = json.loads(response.content)
    assert response == {'count': 0, 'next': None, 'previous': None, 'results': []}

    response = api_client.get(url, {
        'state': 'ALL'
    })
    assert response.status_code==200

    response = json.loads(response.content)
    assert response['count'] == 17

    response = api_client.get(url, {
        'state': 'COMPLETE',
        'start_date': '2022-05-23 13:03:06',
        'end_date': '2022-05-23 13:03:48',
        'exported_at': '2022-05-23 13:03:06'
    })
    assert response.status_code==200

    response = json.loads(response.content)
    assert response['count'] == 4
    
    response = api_client.get(url, {
        'state': 'READY'
    })

    response = json.loads(response.content)
    assert response == data['expense_groups_ready_response']

    response = api_client.get(url, {
      'state': 'FAILED'
    })
    response = json.loads(response.content)
    assert response == {'count': 0, 'next': None, 'previous': None, 'results': []}

    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=3,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )
    response = api_client.post(
        url,
        data={'task_log_id': task_log.id},
        format='json'
    )
    assert response.status_code==200


def test_expense_group_settings(api_client, test_connection):
    access_token = test_connection.access_token

    url = reverse('expense-group-settings', 
        kwargs={
                'workspace_id': 3,
            }
        )
    
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
    response = api_client.get(url)
    response = json.loads(response.content)

    assert dict_compare_keys(response, data['expense_groups_settings_response']) == [], 'expense group api return diffs in keys'
    assert response['reimbursable_expense_group_fields'] == ['employee_email', 'report_id', 'project', 'fund_source', 'claim_number']
    assert response['expense_state'] == 'PAYMENT_PROCESSING'
    assert response['reimbursable_export_date_type'] == 'current_date'
    assert response['ccc_expense_state'] == 'PAID'

    response = api_client.post(
        url,
        data=data['expense_group_settings_payload'],
        format='json'
    )
    assert response.status_code==200
    response = json.loads(response.content)

    assert dict_compare_keys(response, data['expense_groups_settings_response']) == [], 'expense group api return diffs in keys'
    assert response['expense_state'] == 'PAID'
    assert response['reimbursable_export_date_type'] == 'spent_at'
    

def test_fyle_refresh_dimension(mocker, api_client, test_connection):
    mocker.patch(
        'fyle_integrations_platform_connector.fyle_integrations_platform_connector.PlatformConnector.import_fyle_dimensions',
        return_value=[]
    )

    access_token = test_connection.access_token

    url = reverse('refresh-fyle-dimensions', 
        kwargs={
                'workspace_id': 1,
            }
        )
    
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
    
    response = api_client.post(url)
    assert response.status_code == 200

    fyle_credentials = FyleCredential.objects.get(workspace_id=1)
    fyle_credentials.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    assert response.data['message'] == 'Fyle credentials not found in workspace'

    with mock.patch('apps.workspaces.models.FyleCredential.objects.get') as mock_call:
        mock_call.side_effect = Exception()
        response = api_client.post(url)
        assert response.status_code == 400


def test_fyle_sync_dimension(mocker, api_client, test_connection, db):
    mocker.patch(
        'fyle_integrations_platform_connector.fyle_integrations_platform_connector.PlatformConnector.import_fyle_dimensions',
        return_value=[]
    )

    access_token = test_connection.access_token

    url = reverse('sync-fyle-dimensions', 
        kwargs={
                'workspace_id': 1,
            }
        )
    
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
    
    response = api_client.post(url)
    assert response.status_code == 200

    workspace = Workspace.objects.get(id=1)
    workspace.source_synced_at = None
    workspace.save()

    response = api_client.post(url)
    assert response.status_code == 200


def test_fyle_sync_dimension_fail(api_client, test_connection):
    
    access_token = test_connection.access_token

    url = reverse('sync-fyle-dimensions', 
        kwargs={
                'workspace_id': 1,
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
    workspace = Workspace.objects.get(id=1)
    workspace.source_synced_at = None
    workspace.save()
    fyle_credentials = FyleCredential.objects.get(workspace_id=1)
    fyle_credentials.delete()

    new_response = api_client.post(url)
    assert new_response.status_code == 400
    assert new_response.data['message'] == 'Fyle credentials not found in workspace'

    with mock.patch('apps.workspaces.models.FyleCredential.objects.get') as mock_call:
        mock_call.side_effect = Exception()
        response = api_client.post(url)
        assert response.status_code == 400


def test_expense_fields_view(api_client, test_connection):
    
    access_token = test_connection.access_token

    url = reverse('expense-fields', 
        kwargs={
                'workspace_id': 3
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response[0] == data['expense_fields_response'][0]

def test_employees_view(api_client, test_connection):
    
    access_token = test_connection.access_token

    url = reverse('employees', 
        kwargs={
                'workspace_id': 3
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200


def test_exportable_expense_groups(api_client, test_connection):
    access_token = test_connection.access_token

    url = reverse('exportable-expense-groups', 
        kwargs={
                'workspace_id': 3
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)
    assert response['exportable_expense_group_ids'] == []


def test_sync_expense_groups(api_client, test_connection):
    access_token = test_connection.access_token

    url = reverse('sync-expense-groups', 
        kwargs={
                'workspace_id': 3
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200


def test_expense_filters(api_client, test_connection):
   access_token=test_connection.access_token

   url = reverse('expense-filters', 
      kwargs={
         'workspace_id': 1,
      }
   )

   api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

   response = api_client.post(url,data=data['expense_filter_1'])
   assert response.status_code == 201
   response = json.loads(response.content)

   assert dict_compare_keys(response, data['expense_filter_1_response']) == [], 'expense group api return diffs in keys'

   response = api_client.post(url,data=data['expense_filter_2'])
   assert response.status_code == 201
   response = json.loads(response.content)

   assert dict_compare_keys(response, data['expense_filter_2_response']) == [], 'expense group api return diffs in keys'

   response = api_client.get(url)
   assert response.status_code == 200
   response = json.loads(response.content)

   assert dict_compare_keys(response, data['expense_filters_response']) == [], 'expense group api return diffs in keys'


@pytest.mark.django_db(databases=['default'])
def test_custom_fields(mocker, api_client, test_connection):
   access_token=test_connection.access_token

   url = reverse('custom-field', 
      kwargs={
         'workspace_id': 1,
      }
   )

   mocker.patch(
      'fyle.platform.apis.v1beta.admin.expense_fields.list_all',
      return_value=data['get_all_custom_fields']
   )

   api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

   response = api_client.get(url)
   assert response.status_code == 200
   response = json.loads(response.content)

   assert dict_compare_keys(response, data['custom_fields_response']) == [], 'expense group api return diffs in keys'


@pytest.mark.django_db(databases=['default'])
def test_expenses(mocker, api_client, test_connection):
   access_token=test_connection.access_token

   url = reverse('expenses', 
      kwargs={
        'workspace_id': 1,
      }
   )
   url = url + "?org_id=orHVw3ikkCxJ"

   api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

   response = api_client.get(url)
   assert response.status_code == 200
   response = json.loads(response.content)

   assert dict_compare_keys(response, data['skipped_expenses']) == [], 'expense group api return diffs in keys'
