from apps.fyle.models import ExpenseGroup
from apps.workspaces.models import FyleCredential
import pytest
import json
from django.urls import reverse
from .fixtures import data
from tests.helper import dict_compare_keys

@pytest.mark.django_db(databases=['default'])
def test_expense_group_view(api_client, test_connection):
   access_token = test_connection.access_token

   url = reverse('expense-groups', 
         kwargs={
               'workspace_id': 8,
            }
         )
   
   api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

   response = api_client.get(url, {
      'state': 'COMPLETE'
   })
   assert response.status_code==200

   response = json.loads(response.content)

   assert response == data['expense_groups_complete_response']
   
   response = api_client.get(url, {
      'state': 'READY'
   })
   response = json.loads(response.content)

   assert response == data['expense_groups_ready_response']

@pytest.mark.django_db(databases=['default'])
def test_count_expense_view(api_client, test_connection):
    access_token = test_connection.access_token

    url = reverse('expense-groups-count', 
        kwargs={
                'workspace_id': 8,
            }
        )
    
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
    response = api_client.get(url,{
        'state':'COMPLETE'
    })
        
    assert response.status_code==200
    assert response.data['count'] == 3

@pytest.mark.django_db(databases=['default'])
def test_expense_group_settings(api_client, test_connection):
    access_token = test_connection.access_token

    url = reverse('expense-group-settings', 
        kwargs={
                'workspace_id': 8,
            }
        )
    
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
    response = api_client.get(url)
    response = json.loads(response.content)

    assert dict_compare_keys(response, data['expense_groups_settings_response']) == [], 'expense group api return diffs in keys'
    assert response['reimbursable_expense_group_fields'] == ['employee_email', 'report_id', 'claim_number', 'fund_source']
    assert response['expense_state'] == 'PAYMENT_PROCESSING'
    assert response['reimbursable_export_date_type'] == 'current_date'

    response = api_client.post(
        url,
        data=data['expense_group_settings_payload'],
        format='json'
    )
    assert response.status_code==200
    response = json.loads(response.content)
    
    assert dict_compare_keys(response, data['expense_groups_settings_response']) == [], 'expense group api return diffs in keys'
    assert response['expense_state'] == 'PAID'
    assert response['reimbursable_export_date_type'] == 'current_date'
    
    

@pytest.mark.django_db(databases=['default'])
def test_fyle_refresh_dimension(api_client, test_connection, add_fyle_credentials):
    
    access_token = test_connection.access_token

    url = reverse('refresh-fyle-dimensions', 
        kwargs={
                'workspace_id': 8,
            }
        )
    
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
    
    response = api_client.post(url)
    assert response.status_code == 200

    fyle_credentials = FyleCredential.objects.get(workspace_id=8)
    fyle_credentials.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    assert response.data['message'] == 'Fyle credentials not found in workspace'

@pytest.mark.django_db(databases=['default'])
def test_fyle_sync_dimension(api_client, test_connection, add_fyle_credentials):
    
    access_token = test_connection.access_token

    url = reverse('sync-fyle-dimensions', 
        kwargs={
                'workspace_id': 8,
            }
        )
    
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
    
    response = api_client.post(url)
    assert response.status_code == 200

# Todo : merge the two sync functions
@pytest.mark.django_db(databases=['default'])
def test_fyle_sync_dimension_fail(api_client, test_connection, add_fyle_credentials):
    
    access_token = test_connection.access_token

    url = reverse('sync-fyle-dimensions', 
        kwargs={
                'workspace_id': 8,
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
    
    fyle_credentials = FyleCredential.objects.get(workspace_id=8)
    fyle_credentials.delete()

    new_response = api_client.post(url)
    assert new_response.status_code == 400
    assert new_response.data['message'] == 'Fyle credentials not found in workspace'

@pytest.mark.django_db(databases=['default'])
def test_expense_group_id_view(api_client, test_connection):
    
    access_token = test_connection.access_token

    expense_group = ExpenseGroup.objects.filter(workspace_id=8).first()
    url = reverse('expense-group-by-id', 
        kwargs={
                'workspace_id': 8,
                'expense_group_id': expense_group.id
            }
        )
    
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['expense_group_id_response']) == [], 'expense group api return diffs in keys'

    url = reverse('expense-group-by-id', 
        kwargs={
                'workspace_id': 8,
                'expense_group_id': 9999
            }
        )
    
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == 'Expense group not found'



@pytest.mark.django_db(databases=['default'])
def test_expense_group_by_id_expenses_view(api_client, test_connection):
    
    access_token = test_connection.access_token

    expense_group = ExpenseGroup.objects.filter(workspace_id=8).first()
    url = reverse('expense-group-by-id-expenses', 
        kwargs={
                'workspace_id': 8,
                'expense_group_id': expense_group.id
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['expense_group_by_id_expenses_response']) == [], 'expense group api return diffs in keys'

    url = reverse('expense-group-by-id-expenses', 
        kwargs={
                'workspace_id': 8,
                'expense_group_id': 443
            }
        )

    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == 'Expense group not found'

@pytest.mark.django_db(databases=['default'])
def test_expense_fields_view(api_client, test_connection):
    
    access_token = test_connection.access_token

    url = reverse('expense-fields', 
        kwargs={
                'workspace_id': 9
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response == data['expense_fields_response']

@pytest.mark.django_db(databases=['default'])
def test_employees_view(api_client, test_connection):
    
    access_token = test_connection.access_token

    url = reverse('employees', 
        kwargs={
                'workspace_id': 9
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response == data['employees_response']

@pytest.mark.django_db(databases=['default'])
def test_categories_view(api_client, test_connection):
    
    access_token = test_connection.access_token

    url = reverse('categories', 
        kwargs={
                'workspace_id': 9
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response == data['categories_response']

@pytest.mark.django_db(databases=['default'])
def test_cost_centers_view(api_client, test_connection):
    
    access_token = test_connection.access_token

    url = reverse('cost-centers', 
        kwargs={
                'workspace_id': 9
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response == data['cost_centers_response']

# Todo: check the response as well for projects
@pytest.mark.django_db(databases=['default'])
def test_projects_view(api_client, test_connection):
    
    access_token = test_connection.access_token

    url = reverse('projects', 
        kwargs={
                'workspace_id': 8
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
