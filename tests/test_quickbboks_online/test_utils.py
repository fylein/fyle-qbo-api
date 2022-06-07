import ast
import os
import pytest
from fyle_accounting_mappings.models import DestinationAttribute
from apps.quickbooks_online.utils import QBOConnector, QBOCredential
from .fixtures import data
from tests.helper import dict_compare_keys
import random  
import string  
import json

vendor_name = ''
QBO_REFRESH_TOKENS = ast.literal_eval(os.environ.get('QBO_REFRESH_TOKENS'))

def update_qbo_refresh_token(workspace_id, refresh_token):
    global QBO_REFRESH_TOKENS 
    QBO_REFRESH_TOKENS[workspace_id] = refresh_token
    os.environ['QBO_REFRESH_TOKENS'] = json.dumps(QBO_REFRESH_TOKENS)


def random_string():
    result = ''.join((random.choice(string.ascii_lowercase) for x in range(15)))
    return result


@pytest.mark.django_db
def test_sync_employees(db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    employee_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='EMPLOYEE').count()
    assert employee_count == 2

    qbo_connection.sync_employees()

    new_employee_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='EMPLOYEE').count()
    assert new_employee_count == 2
    assert 1 == 2


def test_post_vendor(db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=4)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=4)

    vendor = qbo_connection.get_or_create_vendor(vendor_name='test Sharma',email='test@fyle.in', create=True)

    assert vendor.value == 'test Sharma'

    global vendor_name
    vendor_name = random_string()
    vendor = qbo_connection.get_or_create_vendor(vendor_name=vendor_name, email=vendor_name+'@fyle.in', create=True)

    assert vendor.value == vendor_name
    assert 1 == 2


def test_sync_vendors(db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=4)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=4)

    vendor_count = DestinationAttribute.objects.filter(workspace_id=4, attribute_type='VENDOR').count()
    assert vendor_count == 47

    qbo_connection.sync_vendors()

    new_vendor_count = DestinationAttribute.objects.filter(workspace_id=4, attribute_type='VENDOR', value=vendor_name).count()
    assert new_vendor_count == 1


def test_sync_departments(db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    department_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='DEPARTMENT').count()
    assert department_count == 0

    qbo_connection.sync_departments()

    new_department_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='DEPARTMENT').count()
    assert new_department_count == 0

def test_construct_bill(create_bill, db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=4)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=4)

    bill, bill_lineitems = create_bill
    bill_object = qbo_connection._QBOConnector__construct_bill(bill=bill,bill_lineitems=bill_lineitems)

    data['bill_payload']['TxnDate'] = bill_object['TxnDate']

    assert dict_compare_keys(bill_object, data['bill_payload']) == [], 'construct bill_payload entry api return diffs in keys'


def test_construct_credit_card_purchase(create_credit_card_purchase, db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    credit_card_purchase,credit_card_purchase_lineitems = create_credit_card_purchase
    credit_crad_purchase_object = qbo_connection._QBOConnector__construct_credit_card_purchase(credit_card_purchase=credit_card_purchase, credit_card_purchase_lineitems=credit_card_purchase_lineitems)

    data['credit_card_purchase_payload']['TxnDate'] = credit_crad_purchase_object['TxnDate']

    assert dict_compare_keys(credit_crad_purchase_object, data['credit_card_purchase_payload']) == [], 'construct credit_card_purchase_payload entry api return diffs in keys'


def test_construct_journal_entry(create_journal_entry, db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    journal_entry,journal_entry_lineitems = create_journal_entry
    journal_entry_object = qbo_connection._QBOConnector__construct_journal_entry(journal_entry=journal_entry,journal_entry_lineitems=journal_entry_lineitems,single_credit_line=False)

    data['journal_entry_payload']['TxnDate'] = journal_entry_object['TxnDate']

    assert dict_compare_keys(journal_entry_object, data['journal_entry_payload']) == [], 'construct journal entry api return diffs in keys'


def test_construct_qbo_expense(create_qbo_expense, db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    qbo_expense,qbo_expense_lineitems = create_qbo_expense
    qbo_expense_object = qbo_connection._QBOConnector__construct_qbo_expense(qbo_expense=qbo_expense,qbo_expense_lineitems=qbo_expense_lineitems)

    data['qbo_expense_payload']['TxnDate'] = qbo_expense_object['TxnDate']

    assert dict_compare_keys(qbo_expense_object, data['qbo_expense_payload']) == [], 'construct expense api return diffs in keys'


def test_construct_cheque(create_cheque, db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    cheque,cheque_lineitems = create_cheque
    cheque_object = qbo_connection._QBOConnector__construct_cheque(cheque=cheque,cheque_lineitems=cheque_lineitems)

    data['cheque_payload']['TxnDate'] = cheque_object['TxnDate']

    assert dict_compare_keys(cheque_object, data['cheque_payload']) == [], 'construct cheque api return diffs in keys'


def test_get_bill(db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    bill = qbo_connection.get_bill(146)

    assert dict_compare_keys(bill, data['bill_response']) == []


def test_get_effective_tax_rates(db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    effective_tax_rate, tax_rate_refs = qbo_connection.get_effective_tax_rates([{'TaxRateRef': {'value': '5', 'name': 'NO TAX PURCHASE'}, 'TaxTypeApplicable': 'TaxOnAmount', 'TaxOrder': 0}])
    
    print(effective_tax_rate, tax_rate_refs)
    assert effective_tax_rate == 0
    assert tax_rate_refs == [{'name': 'NO TAX PURCHASE', 'value': '5'}]


def test_get_tax_inclusive_amount(db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    tax_inclusive_amount = qbo_connection.get_tax_inclusive_amount(100, 4)
    
    assert tax_inclusive_amount == 100.0


def test_sync_tax_codes(db):
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    tax_code_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='TAX_CODE').count()
    assert tax_code_count == 1

    qbo_connection.sync_tax_codes()

    new_tax_code_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='TAX_CODE').count()
    assert new_tax_code_count == 1


def tests_sync_accounts(db):

    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    account_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='ACCOUNTS_PAYABLE').count()
    assert account_count == 87

    qbo_connection.sync_accounts()

    new_account_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='ACCOUNTS_PAYABLE').count()
    assert new_account_count == 87
    

def test_sync_dimensions(db):
    employee_count = DestinationAttribute.objects.filter(attribute_type='EMPLOYEE', workspace_id=1).count()
    project_count = DestinationAttribute.objects.filter(attribute_type='PROJECT', workspace_id=1).count()
    categoty_count = DestinationAttribute.objects.filter(attribute_type='EXPENSE_CATEGORY', workspace_id=1).count()

    assert employee_count == 2
    assert project_count == 0
    assert categoty_count == 0

    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    qbo_connection.sync_dimensions()

    employee_count = DestinationAttribute.objects.filter(attribute_type='EMPLOYEE', workspace_id=1).count()
    project_count = DestinationAttribute.objects.filter(attribute_type='PROJECT', workspace_id=1).count()
    categoty_count = DestinationAttribute.objects.filter(attribute_type='EXPENSE_CATEGORY', workspace_id=1).count()

    assert employee_count == 2
    assert project_count == 0
    assert categoty_count == 0
