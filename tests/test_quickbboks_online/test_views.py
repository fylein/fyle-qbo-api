from os import access
from django.urls import reverse
import pytest
import json
from apps.tasks.models import TaskLog
from apps.workspaces.models import QBOCredential
from apps.fyle.models import Reimbursement

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


def test_get_company_preference(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/preferences/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert response['Id'] == '1'

    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.get(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_post_company_preference(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/preferences/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200


def test_get_company_info(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/company_info/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert response['CompanyName'] == 'Sandbox Company_US_4'

    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.get(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_get_vendor_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/vendors/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 29


def test_post_vendor_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/vendors/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0

    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_get_employee_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/employees/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 2


def test_post_employee_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/employees/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_get_account_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/accounts/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 63


def test_post_account_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/accounts/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_get_credit_card_account_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/credit_card_accounts/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 2


def test_post_credit_card_account_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/credit_card_accounts/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_get_bank_account_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bank_accounts/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 2


def test_post_bank_account_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bank_accounts/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_get_accounts_payable_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/accounts_payables/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 87


def test_post_accounts_payable_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/accounts_payables/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_get_bill_payment_account_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bill_payment_accounts/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 2


def test_post_bill_payment_account_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bill_payment_accounts/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_get_classe_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/classes/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0


def test_post_classe_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/classes/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_get_department_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/departments/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0


def test_post_department_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/departments/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


def test_get_customer_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/customers/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 29


def test_post_customer_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/customers/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
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


def test_get_bill_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bills/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 4


def test_post_bill_view(api_client, test_connection):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bills/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_id': 14,
            'task_log_id': task_log.id
        })
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


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


def test_get_cheque_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/checks/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 4


def test_post_cheque_view(api_client, test_connection):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/checks/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_id': 14,
            'task_log_id': task_log.id
        })
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


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


def test_get_credit_card_purchase_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/credit_card_purchases/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 4


def test_post_credit_card_purchase_view(api_client, test_connection):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/credit_card_purchases/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_id': 14,
            'task_log_id': task_log.id
        })
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


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


def test_get_journal_entrie_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/journal_entries/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 4


def test_post_journal_entrie_view(api_client, test_connection):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/journal_entries/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_id': 14,
            'task_log_id': task_log.id
        })
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 0
     
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


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


def test_create_bill_payment(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/bill_payments/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)

    assert response.status_code == 200


def test_post_reimburse_payments(api_client, test_connection):

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


def test_post_refresh_dimensions(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/refresh_dimensions/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    
    assert response.status_code == 200
         
    qbo_credential = QBOCredential.objects.get(workspace_id=3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'Quickbooks credentials not found in workspace'


def test_post_update_grouping_on_department(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/update_grouping_on_department/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    
    assert response.status_code == 200