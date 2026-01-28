import copy
import json

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from tests.helper import dict_compare_keys
from tests.test_workspaces.test_apis.test_export_settings.fixtures import data


def test_export_settings(api_client, test_connection):
    workspace = Workspace.objects.get(id=3)
    workspace.onboarding_state = 'EXPORT_SETTINGS'
    workspace.save()

    workspace_general_settings_instance = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    workspace_general_settings_instance.map_merchant_to_vendor = True
    workspace_general_settings_instance.category_sync_version = 'v2'
    workspace_general_settings_instance.save()

    url = '/api/v2/workspaces/3/export_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.put(url, data=data['export_settings'], format='json')

    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['response']) == [], 'workspaces api returns a diff in the keys'

    invalid_workspace_general_settings = copy.deepcopy(data['export_settings'])
    invalid_workspace_general_settings['workspace_general_settings'] = {}
    response = api_client.put(url, data=invalid_workspace_general_settings, format='json')

    assert response.status_code == 400

    invalid_expense_group_settings = copy.deepcopy(data['export_settings'])
    invalid_expense_group_settings['expense_group_settings'] = {}
    invalid_expense_group_settings['workspace_general_settings'] = {'reimbursable_expenses_object': 'EXPENSE', 'corporate_credit_card_expenses_object': 'BILL'}

    response = api_client.put(url, data=invalid_expense_group_settings, format='json')

    assert response.status_code == 400


def test_export_settings_validation(api_client, test_connection):
    url = '/api/v2/workspaces/3/export_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    # Test BILL type reimbursable expenses validation
    bill_settings = copy.deepcopy(data['export_settings'])
    bill_settings['workspace_general_settings']['reimbursable_expenses_object'] = 'BILL'
    bill_settings['workspace_general_settings']['corporate_credit_card_expenses_object'] = 'EXPENSE'  # Set to different value to avoid conflict
    bill_settings['general_mappings']['accounts_payable'] = {'id': '', 'name': ''}
    response = api_client.put(url, data=bill_settings, format='json')
    assert response.status_code == 400
    assert 'Accounts Payable is required for BILL type reimbursable expenses' in str(response.content)

    # Test CHECK type reimbursable expenses validation
    check_settings = copy.deepcopy(data['export_settings'])
    check_settings['workspace_general_settings']['reimbursable_expenses_object'] = 'CHECK'
    check_settings['workspace_general_settings']['corporate_credit_card_expenses_object'] = 'EXPENSE'  # Set to different value to avoid conflict
    check_settings['general_mappings']['bank_account'] = {'id': '', 'name': ''}
    response = api_client.put(url, data=check_settings, format='json')
    assert response.status_code == 400
    assert 'Bank Account is required for CHECK type reimbursable expenses' in str(response.content)

    # Test EXPENSE type reimbursable expenses validation
    expense_settings = copy.deepcopy(data['export_settings'])
    expense_settings['workspace_general_settings']['reimbursable_expenses_object'] = 'EXPENSE'
    expense_settings['workspace_general_settings']['corporate_credit_card_expenses_object'] = 'BILL'  # Set to different value to avoid conflict
    expense_settings['general_mappings']['qbo_expense_account'] = {'id': '', 'name': ''}
    response = api_client.put(url, data=expense_settings, format='json')
    assert response.status_code == 400
    assert 'Expense Payment Account is required for EXPENSE type reimbursable expenses' in str(response.content)

    # Test JOURNAL ENTRY type with VENDOR mapping validation
    je_vendor_settings = copy.deepcopy(data['export_settings'])
    je_vendor_settings['workspace_general_settings']['reimbursable_expenses_object'] = 'JOURNAL ENTRY'
    je_vendor_settings['workspace_general_settings']['corporate_credit_card_expenses_object'] = None
    je_vendor_settings['workspace_general_settings']['employee_field_mapping'] = 'VENDOR'
    je_vendor_settings['general_mappings']['accounts_payable'] = {'id': '', 'name': ''}
    response = api_client.put(url, data=je_vendor_settings, format='json')
    assert response.status_code == 400
    assert 'Accounts Payable is required for JOURNAL ENTRY with VENDOR mapping' in str(response.content)

    # Test JOURNAL ENTRY type with EMPLOYEE mapping validation
    je_employee_settings = copy.deepcopy(data['export_settings'])
    je_employee_settings['workspace_general_settings']['employee_field_mapping'] = 'EMPLOYEE'
    je_employee_settings['workspace_general_settings']['reimbursable_expenses_object'] = 'JOURNAL ENTRY'
    je_employee_settings['workspace_general_settings']['corporate_credit_card_expenses_object'] = None
    je_employee_settings['general_mappings']['bank_account'] = {'id': '', 'name': ''}
    response = api_client.put(url, data=je_employee_settings, format='json')
    assert response.status_code == 400
    assert 'Bank Account is required for JOURNAL ENTRY with EMPLOYEE mapping' in str(response.content)

    # Test BILL type corporate credit card expenses validation
    ccc_bill_settings = copy.deepcopy(data['export_settings'])
    ccc_bill_settings['workspace_general_settings']['corporate_credit_card_expenses_object'] = 'BILL'
    ccc_bill_settings['workspace_general_settings']['reimbursable_expenses_object'] = None  # Set to different value to avoid conflict
    ccc_bill_settings['general_mappings']['accounts_payable'] = {'id': '', 'name': ''}
    ccc_bill_settings['general_mappings']['default_ccc_vendor'] = {'id': '', 'name': ''}
    response = api_client.put(url, data=ccc_bill_settings, format='json')
    assert response.status_code == 400
    assert 'Accounts Payable is required for BILL type corporate credit card expenses' in str(response.content)

    # Test CREDIT CARD PURCHASE type validation
    ccp_settings = copy.deepcopy(data['export_settings'])
    ccp_settings['workspace_general_settings']['corporate_credit_card_expenses_object'] = 'CREDIT CARD PURCHASE'
    ccp_settings['workspace_general_settings']['reimbursable_expenses_object'] = None
    ccp_settings['general_mappings']['default_ccc_account'] = {'id': '', 'name': ''}
    response = api_client.put(url, data=ccp_settings, format='json')
    assert response.status_code == 400
    assert 'Default Credit Card Account is required for CREDIT CARD PURCHASE type expenses' in str(response.content)

    # Test DEBIT CARD EXPENSE type validation
    debit_settings = copy.deepcopy(data['export_settings'])
    debit_settings['workspace_general_settings']['corporate_credit_card_expenses_object'] = 'DEBIT CARD EXPENSE'
    debit_settings['workspace_general_settings']['reimbursable_expenses_object'] = None
    debit_settings['general_mappings']['default_debit_card_account'] = {'id': '', 'name': ''}
    response = api_client.put(url, data=debit_settings, format='json')
    assert response.status_code == 400
    assert 'Default Debit Card Account is required for DEBIT CARD EXPENSE type expenses' in str(response.content)

    # Test JOURNAL ENTRY with MERCHANT name validation
    je_merchant_settings = copy.deepcopy(data['export_settings'])
    je_merchant_settings['workspace_general_settings']['corporate_credit_card_expenses_object'] = 'JOURNAL ENTRY'
    je_merchant_settings['workspace_general_settings']['name_in_journal_entry'] = 'MERCHANT'
    je_merchant_settings['workspace_general_settings']['reimbursable_expenses_object'] = None
    je_merchant_settings['general_mappings']['default_ccc_account'] = {'id': '', 'name': ''}
    response = api_client.put(url, data=je_merchant_settings, format='json')
    assert response.status_code == 400
    assert 'Default Credit Card Account is required for JOURNAL ENTRY with MERCHANT name' in str(response.content)
