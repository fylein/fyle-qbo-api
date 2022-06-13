from pkg_resources import working_set
import pytest
import json
from django.urls import reverse

from apps.mappings.models import GeneralMapping
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.workspaces.models import Workspace
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
    assert response['qbo_expense_account_name'] == 'Checking'
    assert response['default_ccc_vendor_name'] ==  None

    general_mapping = GeneralMapping.objects.get(workspace_id=3)
    general_mapping.default_ccc_vendor_name = ''
    general_mapping.use_employee_department = True
    general_mapping.save()
    response = api_client.get(url)

    GeneralMapping.objects.get(workspace_id=3).delete()

    response = api_client.get(url)

    assert response.status_code == 400
    assert response.data['message'] == 'General mappings do not exist for the workspace'


@pytest.mark.django_db(databases=['default'])
def test_post_general_mappings(api_client, test_connection):
    '''
    Test get of general mappings
    '''
    url = '/api/workspaces/3/mappings/general/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    payload = data['general_mapping_payload']
    response = api_client.post(
        url,
        data=payload,
    )

    assert response.status_code == 200
    response = json.loads(response.content)
    assert response['accounts_payable_id'] == '33'

    invalid_data = data['general_mapping_payload']

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)

    general_settings.corporate_credit_card_expenses_object = 'BILL'
    general_settings.save()

    response = api_client.post(
        url,
        data=payload
    )
    
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['message'] == 'default ccc vendor id field is blank'

    general_settings.reimbursable_expenses_object = 'BILL'
    general_settings.employee_field_mapping == 'EMPLOYEE'
    general_settings.save()

    response = api_client.post(
        url,
        data=invalid_data
    )
    
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['message'] == 'default ccc vendor id field is blank'

    general_settings.sync_fyle_to_qbo_payments = True
    general_settings.save()
    
    invalid_data['default_ccc_vendor_id'] = '10'
    response = api_client.post(
        url,
        data=invalid_data
    )

    assert response.status_code == 200
    response = json.loads(response.content)
    assert response['default_ccc_vendor_id'] == '10'

    general_settings.corporate_credit_card_expenses_object == 'DEBIT CARD EXPENSE'
    general_settings.save()
    
    response = api_client.post(
        url,
        data=invalid_data
    )
    assert response.status_code == 200
    response = json.loads(response.content)
    assert response['default_debit_card_account_name'] == 'Sample'


def test_auto_map_employee(api_client, test_connection):

    url = '/api/workspaces/3/mappings/auto_map_employees/trigger/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(url)

    assert response.status_code == 200

    general_mapping = GeneralMapping.objects.get(workspace_id=3)
    general_mapping.delete()

    response = api_client.post(url)

    assert response.status_code == 400
    