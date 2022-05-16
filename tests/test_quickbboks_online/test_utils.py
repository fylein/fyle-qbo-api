import pytest

from fyle_accounting_mappings.models import DestinationAttribute
from apps.quickbooks_online.utils import QBOConnector, QBOCredential
from .fixtures import data
from tests.helper import dict_compare_keys

@pytest.mark.django_db
def test_sync_employees(add_qbo_credentials):
    qbo_credentials = QBOCredential.objects.get(workspace_id=8)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=8)

    employee_count = DestinationAttribute.objects.filter(workspace_id=8, attribute_type='EMPLOYEE').count()
    assert employee_count == 11

    qbo_connection.sync_employees()

    new_employee_count = DestinationAttribute.objects.filter(workspace_id=8, attribute_type='EMPLOYEE').count()
    assert new_employee_count == 11


def test_post_vendor(add_qbo_credentials):
    qbo_credentials = QBOCredential.objects.get(workspace_id=9)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=9)

    vendor = qbo_connection.get_or_create_vendor(vendor_name='test Sharma',email='test@fyle.in', create=True)

    assert vendor.value == 'test Sharma'

def test_sync_vendors(add_qbo_credentials):
    qbo_credentials = QBOCredential.objects.get(workspace_id=9)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=9)

    vendor_count = DestinationAttribute.objects.filter(workspace_id=9, attribute_type='VENDOR').count()
    assert vendor_count == 28

    qbo_connection.sync_vendors()

    new_vendor_count = DestinationAttribute.objects.filter(workspace_id=9, attribute_type='VENDOR').count()
    assert new_vendor_count == 29


def test_sync_departments(add_qbo_credentials):
    qbo_credentials = QBOCredential.objects.get(workspace_id=8)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=8)

    department_count = DestinationAttribute.objects.filter(workspace_id=8, attribute_type='DEPARTMENT').count()
    assert department_count == 4

    qbo_connection.sync_vendors()

    new_department_count = DestinationAttribute.objects.filter(workspace_id=8, attribute_type='DEPARTMENT').count()
    assert new_department_count == 4

def test_construct_bill(add_qbo_credentials,create_bill):
    qbo_credentials = QBOCredential.objects.get(workspace_id=9)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=9)

    bill, bill_lineitems = create_bill
    bill_object = qbo_connection._QBOConnector__construct_bill(bill=bill,bill_lineitems=bill_lineitems)

    data['bill_payload']['TxnDate'] = bill_object['TxnDate']

    assert bill_object == data['bill_payload']

def test_construct_credit_card_purchase(add_qbo_credentials,create_credit_card_purchase):
    qbo_credentials = QBOCredential.objects.get(workspace_id=9)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=9)

    credit_card_purchase,credit_card_purchase_lineitems = create_credit_card_purchase
    credit_crad_purchase_object = qbo_connection._QBOConnector__construct_credit_card_purchase(credit_card_purchase=credit_card_purchase, credit_card_purchase_lineitems=credit_card_purchase_lineitems)

    data['credit_card_purchase_payload']['TxnDate'] = credit_crad_purchase_object['TxnDate']

    assert credit_crad_purchase_object == data['credit_card_purchase_payload']

def test_construct_journal_entry(add_qbo_credentials,create_journal_entry):
    qbo_credentials = QBOCredential.objects.get(workspace_id=8)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=8)

    journal_entry,journal_entry_lineitems = create_journal_entry
    journal_entry_object = qbo_connection._QBOConnector__construct_journal_entry(journal_entry=journal_entry,journal_entry_lineitems=journal_entry_lineitems,single_credit_line=False)

    data['journal_entry_payload']['TxnDate'] = journal_entry_object['TxnDate']

    assert journal_entry_object == data['journal_entry_payload']


def test_construct_qbo_expense(add_qbo_credentials,create_qbo_expense):
    qbo_credentials = QBOCredential.objects.get(workspace_id=8)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=8)

    qbo_expense,qbo_expense_lineitems = create_qbo_expense
    qbo_expense_object = qbo_connection._QBOConnector__construct_qbo_expense(qbo_expense=qbo_expense,qbo_expense_lineitems=qbo_expense_lineitems)

    data['qbo_expense_payload']['TxnDate'] = qbo_expense_object['TxnDate']

    assert qbo_expense_object == data['qbo_expense_payload']


def test_construct_cheque(add_qbo_credentials,create_cheque):
    qbo_credentials = QBOCredential.objects.get(workspace_id=8)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=8)

    cheque,cheque_lineitems = create_cheque
    cheque_object = qbo_connection._QBOConnector__construct_cheque(cheque=cheque,cheque_lineitems=cheque_lineitems)

    data['cheque_payload']['TxnDate'] = cheque_object['TxnDate']

    assert cheque_object == data['cheque_payload']

def test_get_bill(add_qbo_credentials):
    qbo_credentials = QBOCredential.objects.get(workspace_id=8)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=8)

    bill = qbo_connection.get_bill(146)

    assert dict_compare_keys(bill, data['bill_response']) == []
