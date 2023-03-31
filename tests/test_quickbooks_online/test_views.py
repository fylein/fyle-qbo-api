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

#  Will use paramaterize decorator of python later
def test_quickbooks_fields_view(api_client, test_connection):

   access_token = test_connection.access_token
   url = reverse('quickbooks-fields', 
      kwargs={
            'workspace_id': 3
         }
      )

   api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

   response = api_client.get(url)
   assert response.status_code == 200
   response = json.loads(response.content)

   assert len(response) == 1

def test_destination_attributes_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = reverse('destination-attributes', 
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

    assert len(response) == 29

def test_searched_destination_attributes_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = reverse('searching-destination-attributes', 
        kwargs={
                'workspace_id': 3
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url,{
        'attribute_type':'CUSTOMER'
    })
    assert response.status_code == 200
    response = json.loads(response.content)
    assert len(response) == 29


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


def test_post_company_preference(mocker, api_client, test_connection):
    mocker.patch(
        'qbosdk.apis.CompanyInfo.get',
        return_value=data['company_info']
    )
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/preferences/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200


def test_post_company_preference_exception(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/preferences/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    with mock.patch('qbosdk.apis.CompanyInfo.get') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='wrong params', response='invalid_params')
        response = api_client.post(url)
        assert response.status_code == 400


def test_get_company_info(mocker, api_client, test_connection):
    mocker.patch(
        'qbosdk.apis.CompanyInfo.get',
        return_value=data['company_info']
    )
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/company_info/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert response['CompanyName'] == 'Sandbox Company_US_4'

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.get_company_info') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='wrong params', response='invalid_params')
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


def test_account_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_accounts',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/accounts/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    
    response = json.loads(response.content)
    assert len(response) == 63

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


def test_credit_card_account_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_accounts',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/credit_card_accounts/'

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


def test_bank_account_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_accounts',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bank_accounts/'

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


def test_accounts_payable_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_accounts',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/accounts_payables/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 87

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


def test_bill_payment_account_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_accounts',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bill_payment_accounts/'

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


def test_classe_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_classes',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/classes/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0

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


def test_department_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_departments',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/departments/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0

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


def test_customer_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_customers',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/customers/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 29

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


def test_get_tax_code_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/tax_codes/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 1


def test_bill_view(api_client, test_connection):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bills/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 4

    response = api_client.post(
        url,
        data={
            'expense_group_id': 14,
            'task_log_id': task_log.id
        })
    assert response.status_code == 200


def test_bill_schedule(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bills/trigger/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_ids': [14],
        })
    assert response.status_code == 200


def test_expense_schedule(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/expenses/trigger/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_ids': [14],
        })
    assert response.status_code == 200


def test_cheque_view(api_client, test_connection):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/checks/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 4

    response = api_client.post(
        url,
        data={
            'expense_group_id': 14,
            'task_log_id': task_log.id
        })
    assert response.status_code == 200


def test_cheque_schedule(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/checks/trigger/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_ids': [14],
        })
    assert response.status_code == 200


def test_credit_card_purchase_view(api_client, test_connection):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/credit_card_purchases/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 4

    response = api_client.post(
        url,
        data={
            'expense_group_id': 14,
            'task_log_id': task_log.id
        })
    assert response.status_code == 200


def test_credit_card_purchase_schedule(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/credit_card_purchases/trigger/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_ids': [14],
        })
    assert response.status_code == 200


def test_debit_card_purchase_schedule(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/debit_card_expenses/trigger/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_ids': [14],
        })
    assert response.status_code == 200


def test_journal_entrie_view(api_client, test_connection):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/journal_entries/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 4

    response = api_client.post(
        url,
        data={
            'expense_group_id': 14,
            'task_log_id': task_log.id
        })
    assert response.status_code == 200


def test_journal_entrie_schedule(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/journal_entries/trigger/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_ids': [14],
        })
    assert response.status_code == 200


def test_create_bill_payment(mocker, api_client, test_connection):
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Reimbursements.sync',
        return_value=None
    )

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bill_payments/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)

    assert response.status_code == 200


def test_post_reimburse_payments(mocker, api_client, test_connection):
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Reimbursements.sync',
        return_value=None
    )

    reimbursements = Reimbursement.objects.all().delete()
    
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/reimburse_payments/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    
    assert response.status_code == 200


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

    assert response['message'] == 'Quickbooks Credentials not found / expired in workspace'


def test_post_update_grouping_on_department(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/update_grouping_on_department/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    
    assert response.status_code == 200
    