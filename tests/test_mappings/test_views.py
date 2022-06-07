import pytest
import json
from django.urls import reverse

from apps.mappings.models import GeneralMapping
from apps.workspaces.models import WorkspaceGeneralSettings
from .fixtures import data


@pytest.mark.django_db(databases=['default'])
def test_get_general_mappings(api_client, test_connection):
    '''
    Test get of general mappings
    '''
    url = '/api/workspaces/3/mappings/general/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)
    print(response)
    assert response['qbo_expense_account_name'] == 'Checking'
    assert response['default_ccc_vendor_name'] ==  None

    general_mapping = GeneralMapping.objects.get(workspace_id=3)
    general_mapping.default_ccc_vendor_name = ''
    general_mapping.use_employee_department = True
    general_mapping.save()
    response = api_client.get(url)

    GeneralMapping.objects.get(workspace_id=3).delete()

    response = api_client.get(url)
    print(response)

    assert response.status_code == 400
    assert response.data['message'] == 'General mappings do not exist for the workspace'


@pytest.mark.django_db(databases=['default'])
def test_post_general_mappings(api_client, test_connection):
    '''
    Test get of general mappings
    '''
    url = '/api/workspaces/3/mappings/general/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(
        url,
        data=data['general_mapping_payload']
    )

    assert response.status_code == 201
    response = json.loads(response.content)
    assert response['use_employee_department'] == True
    assert response['use_employee_class'] == True

    invalid_data = data['general_mapping_payload']

    invalid_data['accounts_payable_name'] = ''
    response = api_client.post(
        url,
        data=invalid_data
    )

    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['non_field_errors'][0] == 'Accounts payable is missing'

    invalid_data['accounts_payable_name'] = 'Accounts Payable'
    invalid_data['reimbursable_account_name'] = ''

    response = api_client.post(
        url,
        data=invalid_data
    )
    
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['non_field_errors'][0] == 'Reimbursable account is missing'

    invalid_data['reimbursable_account_name'] = 'Unapproved Expense Reports'
    invalid_data['default_ccc_vendor_name'] = ''

    response = api_client.post(
        url,
        data=invalid_data
    )
    
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['non_field_errors'][0] == 'Default CCC vendor is missing'

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    general_settings.corporate_credit_card_expenses_object = 'CREDIT CARD CHARGE'
    general_settings.save()

    invalid_data['default_ccc_vendor_name'] = 'Ashwin Vendor'
    invalid_data['default_ccc_account_name'] = ''
    
    response = api_client.post(
        url,
        data=invalid_data
    )
    
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['non_field_errors'][0] == 'Default CCC account is missing'

    invalid_data['default_ccc_account_name'] = 'sample'
    invalid_data['default_ccc_account_id'] = '12'

    general_settings.sync_fyle_to_netsuite_payments = True
    general_settings.save()

    response = api_client.post(
        url,
        data=invalid_data
    )
    
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['non_field_errors'][0] == 'Vendor payment account is missing'

    general_settings.sync_fyle_to_netsuite_payments = False
    general_settings.save()

    invalid_data['default_ccc_account_name'] = 'sample'
    invalid_data['default_ccc_account_id'] = '12'
    invalid_data['department_level'] = ''
    
    response = api_client.post(
        url,
        data=invalid_data
    )
    
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['non_field_errors'][0] == 'department_level cannot be null'

    general_settings.employee_field_mapping = 'VENDOR'
    general_settings.save()
    
    response = api_client.post(
        url,
        data=invalid_data
    )
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['non_field_errors'][0] == 'use_employee_department or use_employee_location or use_employee_class can be used only when employee is mapped to employee'
