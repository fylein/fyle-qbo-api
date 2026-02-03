import json
import logging
from datetime import datetime, timedelta
from unittest import mock

import pytest
from django.utils import timezone
from fyle.platform.exceptions import NoPrivilegeError
from qbosdk.exceptions import WrongParamsError

from apps.fyle.models import ExpenseGroup
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.models import QBOAttributesCount, QBOSyncTimestamp
from apps.quickbooks_online.utils import QBOConnector, QBOCredential, Workspace, WorkspaceGeneralSettings
from fyle_accounting_mappings.models import CategoryMapping, DestinationAttribute, EmployeeMapping, Mapping, MappingSetting
from tests.helper import dict_compare_keys
from tests.test_quickbooks_online.fixtures import data

logger = logging.getLogger(__name__)


def sort_lines(expense):
    """Helper function to sort the Line items by DetailType."""
    if 'Line' in expense:
        expense['Line'] = sorted(expense['Line'], key=lambda x: x['DetailType'])
    return expense


@pytest.mark.django_db
def test_sync_employees(mocker, db):
    """
    Test sync_employees function covering both initial sync and subsequent sync scenarios
    """
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch('qbosdk.apis.Employees.count', return_value=10)
    mock_get_all_generator = mocker.patch('qbosdk.apis.Employees.get_all_generator', return_value=[data['employee_response']])
    mocker.patch('qbosdk.apis.Employees.get_inactive', return_value=[])

    qbo_sync_timestamp = QBOSyncTimestamp.objects.get(workspace_id=workspace_id)

    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='EMPLOYEE').count() == 2

    qbo_sync_timestamp.employee_synced_at = None

    qbo_connection.sync_employees()

    mock_get_all_generator.assert_called_with(None)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='EMPLOYEE').count() == 3

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=True)
    mock_get_all_generator.reset_mock()
    previous_sync_time = timezone.now() - timedelta(days=5)
    qbo_sync_timestamp.employee_synced_at = previous_sync_time
    qbo_sync_timestamp.save()
    mock_get_all_generator.return_value = [data['employee_response_after_sync']]
    mock_get_inactive = mocker.patch('qbosdk.apis.Employees.get_inactive', return_value=[data['employee_response_with_inactive_values']])

    qbo_connection.sync_employees()

    expected_sync_after = (previous_sync_time - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    mock_get_all_generator.assert_called_with(expected_sync_after)
    mock_get_inactive.assert_called_with(expected_sync_after)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='EMPLOYEE').count() == 5
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='EMPLOYEE', active=False).count() == 1

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=False)
    qbo_connection.sync_employees()
    mock_get_all_generator.assert_called_with(None)


def test_post_vendor(mocker, db):
    mocker.patch('qbosdk.apis.Vendors.search_vendor_by_display_name', return_value=[])
    mocker.patch('qbosdk.apis.Vendors.post', return_value=data['post_vendor_resp'])
    qbo_credentials = QBOCredential.get_active_qbo_credentials(4)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=4)

    DestinationAttribute.objects.filter(workspace_id=4, attribute_type='VENDOR', value='test Sharma').delete()

    vendor = qbo_connection.get_or_create_vendor(vendor_name='test Sharma', email='test@fyle.in', create=True)

    assert vendor.value == 'samp_merchant'


def test_sync_vendors(mocker, db):
    """
    Test sync_vendors function covering both initial sync and subsequent sync scenarios
    """
    workspace_id = 4
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch('qbosdk.apis.Vendors.count', return_value=10)
    mock_get_all_generator = mocker.patch('qbosdk.apis.Vendors.get_all_generator', return_value=[data['vendor_response']])
    mocker.patch('qbosdk.apis.Vendors.get_inactive', return_value=[])

    qbo_sync_timestamp = QBOSyncTimestamp.objects.get(workspace_id=workspace_id)

    vendor_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count()
    assert vendor_count == 47

    qbo_sync_timestamp.vendor_synced_at = None
    qbo_sync_timestamp.save()

    qbo_connection.sync_vendors()

    mock_get_all_generator.assert_called_with(None)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count() == 47

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=True)
    mock_get_all_generator.reset_mock()
    previous_sync_time = timezone.now() - timedelta(days=5)
    qbo_sync_timestamp.vendor_synced_at = previous_sync_time
    qbo_sync_timestamp.save()
    mock_get_all_generator.return_value = [data['vendor_response_after_sync']]

    qbo_connection.sync_vendors()

    expected_sync_after = (previous_sync_time - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    mock_get_all_generator.assert_called_with(expected_sync_after)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count() == 48

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=False)
    qbo_connection.sync_vendors()
    mock_get_all_generator.assert_called_with(None)


def test_sync_departments(mocker, db):
    """
    Test sync_departments function covering both initial sync and subsequent sync scenarios
    """
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch('qbosdk.apis.Departments.count', return_value=10)
    mocker.patch('qbosdk.apis.Departments.get_inactive', return_value=[])
    mock_get_all_generator = mocker.patch('qbosdk.apis.Departments.get_all_generator', return_value=[data['department_response']])

    qbo_sync_timestamp = QBOSyncTimestamp.objects.get(workspace_id=workspace_id)

    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='DEPARTMENT').count() == 0

    qbo_sync_timestamp.department_synced_at = None
    qbo_sync_timestamp.save()

    qbo_connection.sync_departments()

    mock_get_all_generator.assert_called_with(None)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='DEPARTMENT').count() == 1

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=True)
    mock_get_all_generator.reset_mock()
    previous_sync_time = timezone.now() - timedelta(days=5)
    qbo_sync_timestamp.department_synced_at = previous_sync_time
    qbo_sync_timestamp.save()
    mock_get_all_generator.return_value = [data['department_response_after_sync']]
    mock_inactive = mocker.patch('qbosdk.apis.Departments.get_inactive', return_value=[data['department_response_with_inactive_values']])

    qbo_connection.sync_departments()

    expected_sync_after = (previous_sync_time - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    mock_get_all_generator.assert_called_with(expected_sync_after)
    mock_inactive.assert_called_with(expected_sync_after)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='DEPARTMENT').count() == 2
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='DEPARTMENT', active=False).count() == 1

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=False)
    qbo_connection.sync_departments()
    mock_get_all_generator.assert_called_with(None)


def test_sync_items(mocker, db):
    """
    Test sync_items function covering both initial sync and subsequent sync scenarios
    """
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch('qbosdk.apis.Items.count', return_value=0)
    mock_inactive = mocker.patch('qbosdk.apis.Items.get_inactive', return_value=[])
    mock_get_all_generator = mocker.patch('qbosdk.apis.Items.get_all_generator', return_value=[data['items_response']])

    qbo_sync_timestamp = QBOSyncTimestamp.objects.get(workspace_id=workspace_id)

    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Item').count() == 0

    qbo_sync_timestamp.item_synced_at = None
    qbo_sync_timestamp.save()

    qbo_connection.sync_items()
    mock_get_all_generator.assert_called_with(None)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Item', active=True).count() == 4

    mock_inactive.return_value = [data['items_response_with_inactive_values']]

    qbo_connection.sync_items()
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Item', active=True).count() == 2
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Item', active=False).count() == 2

    mock_get_all_generator.return_value = [data['items_response_with_category']]

    qbo_connection.sync_items()

    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Item').count() == 4

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=True)
    previous_sync_time = timezone.now() - timedelta(days=5)
    qbo_sync_timestamp.item_synced_at = previous_sync_time
    qbo_sync_timestamp.save()
    mock_get_all_generator.return_value = [data['items_response_after_sync']]

    qbo_connection.sync_items()

    expected_sync_after = (previous_sync_time - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    mock_get_all_generator.assert_called_with(expected_sync_after)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Item', active=True).count() == 3

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=False)
    qbo_connection.sync_items()
    mock_get_all_generator.assert_called_with(None)


def test_construct_bill(add_destination_attribute_tax_code, create_bill, mocker, db):
    mocker.patch('qbosdk.apis.ExchangeRates.get_by_source', return_value={'Rate': 1.2309})
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    # for account-based line-items
    bill, bill_lineitems = create_bill
    bill_object = qbo_connection._QBOConnector__construct_bill(bill=bill, bill_lineitems=bill_lineitems)
    data['bill_payload']['TxnDate'] = bill_object['TxnDate']

    assert dict_compare_keys(bill_object, data['bill_payload']) == [], 'construct bill_payload entry api return diffs in keys'

    workspace_general_settings.is_multi_currency_allowed = True
    workspace_general_settings.save()

    qbo_credentials.currency = 'CAD'
    qbo_credentials.save()

    data['bill_payload']['ExchangeRate'] = 1.2309

    bill_object = qbo_connection._QBOConnector__construct_bill(bill=bill, bill_lineitems=bill_lineitems)
    data['bill_payload']['TxnDate'] = bill_object['TxnDate']

    assert dict_compare_keys(bill_object, data['bill_payload']) == [], 'construct bill_payload entry api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    bill, bill_lineitems = create_bill
    bill_object = qbo_connection._QBOConnector__construct_bill(bill=bill, bill_lineitems=bill_lineitems)

    assert dict_compare_keys(bill_object, data['bill_payload_with_tax_override']) == [], 'construct bill_payload entry api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_bill_item_based(add_destination_attribute_tax_code, create_bill_item_based, mocker, db):
    mocker.patch('qbosdk.apis.ExchangeRates.get_by_source', return_value={'Rate': 1.2309})
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    # for item-based line-items
    bill, bill_lineitems = create_bill_item_based
    bill_object = qbo_connection._QBOConnector__construct_bill(bill=bill, bill_lineitems=bill_lineitems)
    bill_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'

    assert dict_compare_keys(bill_object, data['bill_payload_item_based_payload']) == [], 'construct bill_payload entry api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    bill, bill_lineitems = create_bill_item_based
    bill_object = qbo_connection._QBOConnector__construct_bill(bill=bill, bill_lineitems=bill_lineitems)

    assert dict_compare_keys(bill_object, data['bill_payload_item_based_payload_with_tax_override']) == [], 'construct bill_payload entry api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_bill_item_and_account_based(add_destination_attribute_tax_code, create_bill_item_and_account_based, mocker, db):
    mocker.patch('qbosdk.apis.ExchangeRates.get_by_source', return_value={'Rate': 1.2309})
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    # for item-based and account-based line-items
    bill, bill_lineitems = create_bill_item_and_account_based
    bill_object = qbo_connection._QBOConnector__construct_bill(bill=bill, bill_lineitems=bill_lineitems)
    assert bill_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'
    assert bill_object['Line'][1]['DetailType'] == 'AccountBasedExpenseLineDetail'

    sorted_bill_object = sort_lines(bill_object)
    sorted_expected_payload = sort_lines(data['bill_payload_item_and_account_based_payload'])

    assert dict_compare_keys(sorted_bill_object, sorted_expected_payload) == [], 'construct bill_payload entry api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    bill, bill_lineitems = create_bill_item_and_account_based
    bill_object = qbo_connection._QBOConnector__construct_bill(bill=bill, bill_lineitems=bill_lineitems)
    bill_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'
    bill_object['Line'][1]['DetailType'] == 'AccountBasedExpenseLineDetail'

    assert dict_compare_keys(bill_object, data['bill_payload_item_and_account_based_payload_with_tax_override']) == [], 'construct bill_payload entry api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_credit_card_purchase(add_destination_attribute_tax_code, create_credit_card_purchase, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    credit_card_purchase, credit_card_purchase_lineitems = create_credit_card_purchase
    credit_crad_purchase_object = qbo_connection._QBOConnector__construct_credit_card_purchase(credit_card_purchase=credit_card_purchase, credit_card_purchase_lineitems=credit_card_purchase_lineitems)

    data['credit_card_purchase_payload']['TxnDate'] = credit_crad_purchase_object['TxnDate']

    assert dict_compare_keys(credit_crad_purchase_object, data['credit_card_purchase_payload']) == [], 'construct credit_card_purchase_payload entry api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    credit_crad_purchase_object = qbo_connection._QBOConnector__construct_credit_card_purchase(credit_card_purchase=credit_card_purchase, credit_card_purchase_lineitems=credit_card_purchase_lineitems)

    assert dict_compare_keys(credit_crad_purchase_object, data['credit_card_purchase_payload_with_tax_override']) == [], 'construct credit_card_purchase_payload entry api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_credit_card_purchase_item_based(add_destination_attribute_tax_code, create_credit_card_purchase_item_based, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    credit_card_purchase, credit_card_purchase_lineitems = create_credit_card_purchase_item_based
    credit_crad_purchase_object = qbo_connection._QBOConnector__construct_credit_card_purchase(credit_card_purchase=credit_card_purchase, credit_card_purchase_lineitems=credit_card_purchase_lineitems)

    credit_crad_purchase_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'

    assert dict_compare_keys(credit_crad_purchase_object, data['credit_card_purchase_item_based_payload']) == [], 'construct credit_card_purchase_payload entry api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    credit_card_purchase, credit_card_purchase_lineitems = create_credit_card_purchase_item_based
    credit_crad_purchase_object = qbo_connection._QBOConnector__construct_credit_card_purchase(credit_card_purchase=credit_card_purchase, credit_card_purchase_lineitems=credit_card_purchase_lineitems)

    credit_crad_purchase_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'

    assert dict_compare_keys(credit_crad_purchase_object, data['credit_card_purchase_item_based_payload_with_tax_override']) == [], 'construct credit_card_purchase_payload entry api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_credit_card_purchase_item_and_account_based(add_destination_attribute_tax_code, create_credit_card_purchase_item_and_account_based, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    credit_card_purchase, credit_card_purchase_lineitems = create_credit_card_purchase_item_and_account_based
    credit_crad_purchase_object = qbo_connection._QBOConnector__construct_credit_card_purchase(credit_card_purchase=credit_card_purchase, credit_card_purchase_lineitems=credit_card_purchase_lineitems)

    credit_crad_purchase_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'
    credit_crad_purchase_object['Line'][1]['DetailType'] == 'AccountBasedExpenseLineDetail'

    assert dict_compare_keys(credit_crad_purchase_object, data['credit_card_purchase_item_and_account_based_payload']) == [], 'construct credit_card_purchase_payload entry api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    credit_card_purchase, credit_card_purchase_lineitems = create_credit_card_purchase_item_and_account_based
    credit_crad_purchase_object = qbo_connection._QBOConnector__construct_credit_card_purchase(credit_card_purchase=credit_card_purchase, credit_card_purchase_lineitems=credit_card_purchase_lineitems)

    credit_crad_purchase_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'
    credit_crad_purchase_object['Line'][1]['DetailType'] == 'AccountBasedExpenseLineDetail'

    assert dict_compare_keys(credit_crad_purchase_object, data['credit_card_purchase_item_and_account_based_payload_with_tax_override']) == [], 'construct credit_card_purchase_payload entry api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_journal_entry(create_journal_entry, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()
    general_mappings.default_tax_code_id = 4
    general_mappings.save()

    journal_entry, journal_entry_lineitems = create_journal_entry
    journal_entry_object = qbo_connection._QBOConnector__construct_journal_entry(journal_entry=journal_entry, journal_entry_lineitems=journal_entry_lineitems, single_credit_line=False)

    assert dict_compare_keys(journal_entry_object, data['journal_entry_payload']) == [], 'construct journal entry api return diffs in keys'


def test_construct_qbo_expense(add_destination_attribute_tax_code, create_qbo_expense, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    qbo_expense, qbo_expense_lineitems = create_qbo_expense
    qbo_expense_object = qbo_connection._QBOConnector__construct_qbo_expense(qbo_expense=qbo_expense, qbo_expense_lineitems=qbo_expense_lineitems)

    data['qbo_expense_payload']['TxnDate'] = qbo_expense_object['TxnDate']

    assert dict_compare_keys(qbo_expense_object, data['qbo_expense_payload']) == [], 'construct expense api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    qbo_expense, qbo_expense_lineitems = create_qbo_expense
    qbo_expense_object = qbo_connection._QBOConnector__construct_qbo_expense(qbo_expense=qbo_expense, qbo_expense_lineitems=qbo_expense_lineitems)

    assert dict_compare_keys(qbo_expense_object, data['qbo_expense_payload_with_tax_override']) == [], 'construct expense api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_qbo_expense_item_based(add_destination_attribute_tax_code, create_qbo_expense_item_based, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    qbo_expense, qbo_expense_lineitems = create_qbo_expense_item_based
    qbo_expense_object = qbo_connection._QBOConnector__construct_qbo_expense(qbo_expense=qbo_expense, qbo_expense_lineitems=qbo_expense_lineitems)

    qbo_expense_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'

    assert dict_compare_keys(qbo_expense_object, data['qbo_expense_item_based_payload']) == [], 'construct expense api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    qbo_expense, qbo_expense_lineitems = create_qbo_expense_item_based
    qbo_expense_object = qbo_connection._QBOConnector__construct_qbo_expense(qbo_expense=qbo_expense, qbo_expense_lineitems=qbo_expense_lineitems)

    qbo_expense_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'

    assert dict_compare_keys(qbo_expense_object, data['qbo_expense_item_based_payload_with_tax_override']) == [], 'construct expense api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_qbo_expense_item_and_account_based(add_destination_attribute_tax_code, create_qbo_expense_item_and_account_based, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    qbo_expense, qbo_expense_lineitems = create_qbo_expense_item_and_account_based
    qbo_expense_object = qbo_connection._QBOConnector__construct_qbo_expense(qbo_expense=qbo_expense, qbo_expense_lineitems=qbo_expense_lineitems)

    qbo_expense_object_sorted = sort_lines(qbo_expense_object)
    expected_payload_sorted = sort_lines(data['qbo_expense_item_and_account_based_payload'])

    assert dict_compare_keys(qbo_expense_object_sorted, expected_payload_sorted) == [], 'construct expense api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    qbo_expense, qbo_expense_lineitems = create_qbo_expense_item_and_account_based
    qbo_expense_object = qbo_connection._QBOConnector__construct_qbo_expense(qbo_expense=qbo_expense, qbo_expense_lineitems=qbo_expense_lineitems)

    qbo_expense_object_sorted = sort_lines(qbo_expense_object)
    expected_payload_sorted = sort_lines(data['qbo_expense_item_and_account_based_payload_with_tax_override'])

    assert dict_compare_keys(qbo_expense_object_sorted, expected_payload_sorted) == [], 'construct expense api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_cheque(add_destination_attribute_tax_code, create_cheque, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    cheque, cheque_lineitems = create_cheque
    cheque_object = qbo_connection._QBOConnector__construct_cheque(cheque=cheque, cheque_lineitems=cheque_lineitems)

    data['cheque_payload']['TxnDate'] = cheque_object['TxnDate']

    assert dict_compare_keys(cheque_object, data['cheque_payload']) == [], 'construct cheque api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    cheque, cheque_lineitems = create_cheque
    cheque_object = qbo_connection._QBOConnector__construct_cheque(cheque=cheque, cheque_lineitems=cheque_lineitems)

    assert dict_compare_keys(cheque_object, data['cheque_payload_with_tax_override']) == [], 'construct cheque api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_cheque_item_based(add_destination_attribute_tax_code, create_cheque_item_based, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    cheque, cheque_lineitems = create_cheque_item_based
    cheque_object = qbo_connection._QBOConnector__construct_cheque(cheque=cheque, cheque_lineitems=cheque_lineitems)

    cheque_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'

    assert dict_compare_keys(cheque_object, data['cheque_item_based_payload']) == [], 'construct cheque api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    cheque, cheque_lineitems = create_cheque_item_based
    cheque_object = qbo_connection._QBOConnector__construct_cheque(cheque=cheque, cheque_lineitems=cheque_lineitems)

    cheque_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'

    assert dict_compare_keys(cheque_object, data['cheque_item_based_payload_with_tax_override']) == [], 'construct cheque api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_construct_cheque_item_and_account_based(add_destination_attribute_tax_code, create_cheque_item_and_account_based, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    workspace_general_settings = qbo_credentials.workspace.workspace_general_settings
    workspace_general_settings.import_tax_codes = False
    workspace_general_settings.save()

    cheque, cheque_lineitems = create_cheque_item_and_account_based
    cheque_object = qbo_connection._QBOConnector__construct_cheque(cheque=cheque, cheque_lineitems=cheque_lineitems)

    assert cheque_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'
    assert cheque_object['Line'][1]['DetailType'] == 'AccountBasedExpenseLineDetail'

    assert dict_compare_keys(cheque_object, data['cheque_item_and_account_based_payload']) == [], 'construct cheque api return diffs in keys'

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=3).first()

    general_settings.import_tax_codes = True
    general_settings.save()

    general_mappings.default_tax_code_id = '17'
    general_mappings.default_tax_code_name = 'GST/PST BC @12%'
    general_mappings.save()

    cheque, cheque_lineitems = create_cheque_item_and_account_based
    cheque_object = qbo_connection._QBOConnector__construct_cheque(cheque=cheque, cheque_lineitems=cheque_lineitems)

    assert cheque_object['Line'][0]['DetailType'] == 'ItemBasedExpenseLineDetail'
    assert cheque_object['Line'][1]['DetailType'] == 'AccountBasedExpenseLineDetail'

    assert dict_compare_keys(cheque_object, data['cheque_item_and_account_based_payload_with_tax_override']) == [], 'construct cheque api return diffs in keys'

    general_settings.import_tax_codes = False
    general_settings.save()


def test_get_bill(mocker, db):
    mocker.patch('qbosdk.apis.Bills.get_by_id', return_value=data['bill_response'])
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    bill = qbo_connection.get_bill(146)

    assert dict_compare_keys(bill, data['bill_response']) == []


def test_get_effective_tax_rates(mocker, db):
    mocker.patch('qbosdk.apis.TaxRates.get_by_id', return_value=data['tax_rate_get_by_id'])
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    effective_tax_rate, tax_rate_refs = qbo_connection.get_effective_tax_rates([{'TaxRateRef': {'value': '5', 'name': 'NO TAX PURCHASE'}, 'TaxTypeApplicable': 'TaxOnAmount', 'TaxOrder': 0}])

    assert effective_tax_rate == 2
    assert tax_rate_refs == [{'name': 'NO TAX PURCHASE', 'value': '5', 'taxRate': 2}]


def test_get_tax_inclusive_amount(db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    tax_inclusive_amount = qbo_connection.get_tax_inclusive_amount(100, 4)

    assert tax_inclusive_amount == 100.0


def test_sync_tax_codes(mocker, db):
    """
    Test sync_tax_codes function covering both initial sync and subsequent sync scenarios
    """
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch('qbosdk.apis.TaxCodes.count', return_value=10)
    mock_get_all_generator = mocker.patch('qbosdk.apis.TaxCodes.get_all_generator', return_value=[data['tax_code_response']])
    mocker.patch('qbosdk.apis.TaxCodes.get_inactive', return_value=[])
    mocker.patch('qbosdk.apis.TaxRates.get_by_id', return_value=data['tax_rate_get_by_id'])

    qbo_sync_timestamp = QBOSyncTimestamp.objects.get(workspace_id=workspace_id)

    tax_code_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    assert tax_code_count == 1

    qbo_sync_timestamp.tax_code_synced_at = None
    qbo_sync_timestamp.save()

    qbo_connection.sync_tax_codes()

    mock_get_all_generator.assert_called_with(None)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count() == 2

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=True)
    mock_get_all_generator.reset_mock()
    previous_sync_time = timezone.now() - timedelta(days=5)
    qbo_sync_timestamp.tax_code_synced_at = previous_sync_time
    qbo_sync_timestamp.save()
    mock_get_all_generator.return_value = [data['tax_code_response_after_sync']]
    mock_get_inactive = mocker.patch('qbosdk.apis.TaxCodes.get_inactive', return_value=[data['tax_code_response_with_inactive_values']])

    qbo_connection.sync_tax_codes()

    expected_sync_after = (previous_sync_time - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    mock_get_all_generator.assert_called_with(expected_sync_after)
    mock_get_inactive.assert_called_with(expected_sync_after)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count() == 4
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE', active=False).count() == 1

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=False)
    qbo_connection.sync_tax_codes()
    mock_get_all_generator.assert_called_with(None)


def tests_sync_accounts(mocker, db):
    """
    Test sync_accounts function covering both initial sync and subsequent sync scenarios
    """
    workspace_id = 1
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch('qbosdk.apis.Accounts.count', return_value=10)
    mocker.patch('qbosdk.apis.Accounts.get_inactive', return_value=[])
    mock_get_all_generator = mocker.patch('qbosdk.apis.Accounts.get_all_generator', return_value=[data['account_response']])

    qbo_sync_timestamp = QBOSyncTimestamp.objects.get(workspace_id=workspace_id)

    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT').count() == 63

    qbo_sync_timestamp.account_synced_at = None
    qbo_sync_timestamp.save()

    qbo_connection.sync_accounts()

    mock_get_all_generator.assert_called_with(None)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT').count() == 63

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=True)
    mock_get_all_generator.reset_mock()
    mock_get_all_generator.return_value = [data['account_response_after_sync']]
    previous_sync_time = timezone.now() - timedelta(days=5)
    qbo_sync_timestamp.account_synced_at = previous_sync_time
    qbo_sync_timestamp.save()

    qbo_connection.sync_accounts()
    expected_sync_after = (previous_sync_time - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    mock_get_all_generator.assert_called_with(expected_sync_after)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT').count() == 64

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=False)
    qbo_connection.sync_accounts()
    mock_get_all_generator.assert_called_with(None)


def test_sync_dimensions(mocker, db):
    mocker.patch('qbosdk.apis.Accounts.count', return_value=10)
    mocker.patch('qbosdk.apis.Accounts.get_all_generator')
    mocker.patch('qbosdk.apis.Employees.count', return_value=10)
    mocker.patch('qbosdk.apis.Employees.get_all_generator')
    mocker.patch('qbosdk.apis.Vendors.count', return_value=10)
    mocker.patch('qbosdk.apis.Vendors.get_all_generator')
    mocker.patch('qbosdk.apis.Customers.count', return_value=10)
    mocker.patch('qbosdk.apis.Customers.get_all_generator')
    mocker.patch('qbosdk.apis.Classes.count', return_value=10)
    mocker.patch('qbosdk.apis.Classes.get_all_generator')
    mocker.patch('qbosdk.apis.Departments.count', return_value=10)
    mocker.patch('qbosdk.apis.Departments.get_all_generator')
    mocker.patch('qbosdk.apis.TaxCodes.count', return_value=10)
    mocker.patch('qbosdk.apis.TaxCodes.get_all_generator')
    mocker.patch('qbosdk.apis.Items.count', return_value=10)
    mocker.patch('qbosdk.apis.Items.get_all_generator')

    employee_count = DestinationAttribute.objects.filter(attribute_type='EMPLOYEE', workspace_id=1).count()
    accounts_count = DestinationAttribute.objects.filter(attribute_type='ACCOUNT', workspace_id=1).count()
    vendors_count = DestinationAttribute.objects.filter(attribute_type='VENDOR', workspace_id=1).count()

    assert employee_count == 2
    assert accounts_count == 63
    assert vendors_count == 29

    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)
    qbo_connection.sync_dimensions()

    employee_count = DestinationAttribute.objects.filter(attribute_type='EMPLOYEE', workspace_id=1).count()
    accounts_count = DestinationAttribute.objects.filter(attribute_type='ACCOUNT', workspace_id=1).count()
    vendors_count = DestinationAttribute.objects.filter(attribute_type='VENDOR', workspace_id=1).count()

    assert employee_count == 2
    assert accounts_count == 63
    assert vendors_count == 29


def test_sync_classes(mocker, db):
    """
    Test sync_classes function covering both initial sync and subsequent sync scenarios
    """
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch('qbosdk.apis.Classes.count', return_value=10)
    mocker.patch('qbosdk.apis.Classes.get_inactive', return_value=[])
    mock_get_all_generator = mocker.patch('qbosdk.apis.Classes.get_all_generator', return_value=[data['class_response']])

    qbo_sync_timestamp = QBOSyncTimestamp.objects.get(workspace_id=workspace_id)

    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CLASS').count() == 0

    qbo_sync_timestamp.class_synced_at = None
    qbo_sync_timestamp.save()

    qbo_connection.sync_classes()

    mock_get_all_generator.assert_called_with(None)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CLASS').count() == 2

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=True)
    mock_get_all_generator.reset_mock()
    previous_sync_time = timezone.now() - timedelta(days=5)
    qbo_sync_timestamp.class_synced_at = previous_sync_time
    qbo_sync_timestamp.save()
    mock_get_all_generator.return_value = [data['class_response_after_sync']]
    mock_inactive = mocker.patch('qbosdk.apis.Classes.get_inactive', return_value=[data['class_response_with_inactive_values']])

    qbo_connection.sync_classes()

    expected_sync_after = (previous_sync_time - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    mock_get_all_generator.assert_called_with(expected_sync_after)
    mock_inactive.assert_called_with(expected_sync_after)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CLASS').count() == 3
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CLASS', active=False).count() == 1

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=False)
    qbo_connection.sync_classes()
    mock_get_all_generator.assert_called_with(None)


def test_sync_customers(mocker, db):
    """
    Test sync_customers function covering both initial sync and subsequent sync scenarios
    """
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch('qbosdk.apis.Customers.get_inactive', return_value=[])
    mocker.patch('qbosdk.apis.Customers.count', return_value=5)
    mock_get_all_generator = mocker.patch('qbosdk.apis.Customers.get_all_generator', return_value=[data['class_response']])

    qbo_sync_timestamp = QBOSyncTimestamp.objects.get(workspace_id=workspace_id)

    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CUSTOMER').count() == 29

    qbo_sync_timestamp.customer_synced_at = None
    qbo_sync_timestamp.save()

    qbo_connection.sync_customers()

    mock_get_all_generator.assert_called_with(None)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CUSTOMER').count() == 30

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=True)
    mock_get_all_generator.reset_mock()
    previous_sync_time = timezone.now() - timedelta(days=5)
    qbo_sync_timestamp.customer_synced_at = previous_sync_time
    qbo_sync_timestamp.save()
    mock_get_all_generator.return_value = [data['customer_response_after_sync']]

    qbo_connection.sync_customers()

    expected_sync_after = (previous_sync_time - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    mock_get_all_generator.assert_called_with(expected_sync_after)
    assert DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CUSTOMER').count() == 31

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(is_sync_after_timestamp_enabled=False)
    qbo_connection.sync_customers()
    mock_get_all_generator.assert_called_with(None)


def test_post_bill_exception(mocker, db, create_bill):
    mocker.patch('qbosdk.apis.Bills.post', return_value=data['construct_bill'])
    mocker.patch('qbosdk.apis.Preferences.get', return_value=data['preference_response'])
    workspace_id = 4

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    bill, bill_lineitems = create_bill

    workspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_setting.change_accounting_period = True
    workspace_general_setting.save()

    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    general_settings.import_tax_codes = True
    general_settings.save()

    with mock.patch('qbosdk.apis.Bills.post') as mock_call:
        mock_call.return_value = data['construct_bill']
        mock_call.side_effect = [WrongParamsError(msg='invalid params', response=json.dumps({'Fault': {'Error': [{'code': '6240', 'Message': 'account period closed', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}})), None]
        qbo_connection.post_bill(bill, bill_lineitems)


def test_post_qbo_expense_exception(mocker, db, create_qbo_expense):
    mocker.patch('qbosdk.apis.Preferences.get', return_value=data['preference_response'])
    workspace_id = 4

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    qbo_expense, qbo_expense_lineitems = create_qbo_expense

    workspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_setting.change_accounting_period = True
    workspace_general_setting.save()

    try:
        with mock.patch('qbosdk.apis.Purchases.post') as mock_call:
            mock_call.side_effect = [WrongParamsError(msg='invalid params', response=json.dumps({'Fault': {'Error': [{'code': '6240', 'Message': 'account period closed', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}})), None]
            qbo_connection.post_qbo_expense(qbo_expense, qbo_expense_lineitems)
    except Exception:
        logger.info("Account period error")


def test_post_cheque_exception(mocker, db, create_cheque):
    mocker.patch('qbosdk.apis.Preferences.get', return_value=data['preference_response'])
    workspace_id = 4

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    cheque, cheque_lineitems = create_cheque

    workspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_setting.change_accounting_period = True
    workspace_general_setting.save()

    try:
        with mock.patch('qbosdk.apis.Purchases.post') as mock_call:
            mock_call.side_effect = [WrongParamsError(msg='invalid params', response=json.dumps({'Fault': {'Error': [{'code': '6240', 'Message': 'account period closed', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}})), None]
            qbo_connection.post_cheque(cheque, cheque_lineitems)
    except Exception:
        logger.info("Account period error")


def test_post_credit_card_purchase_exception(mocker, db, create_credit_card_purchase):
    mocker.patch('qbosdk.apis.Preferences.get', return_value=data['preference_response'])
    workspace_id = 4

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    credit_card_purchase, credit_card_purchase_lineitems = create_credit_card_purchase

    workspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_setting.change_accounting_period = True
    workspace_general_setting.save()

    try:
        with mock.patch('qbosdk.apis.Purchases.post') as mock_call:
            mock_call.side_effect = [WrongParamsError(msg='invalid params', response=json.dumps({'Fault': {'Error': [{'code': '6240', 'Message': 'account period closed', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}})), None]
            qbo_connection.post_credit_card_purchase(credit_card_purchase, credit_card_purchase_lineitems)
    except Exception:
        logger.info("Account period error")


def test_post_journal_entry_exception(mocker, db, create_journal_entry):
    mocker.patch('qbosdk.apis.Preferences.get', return_value=data['preference_response'])
    workspace_id = 4

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    journal_entry, journal_entry_lineitems = create_journal_entry

    workspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_setting.change_accounting_period = True
    workspace_general_setting.save()

    try:
        with mock.patch('qbosdk.apis.JournalEntries.post') as mock_call:
            mock_call.side_effect = [WrongParamsError(msg='invalid params', response=json.dumps({'Fault': {'Error': [{'code': '6240', 'Message': 'account period closed', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}})), None]
            qbo_connection.post_journal_entry(journal_entry, journal_entry_lineitems, True)
    except Exception:
        logger.info("Account period error")


def tests_post_bill_payment(mocker, db, create_bill_payment):
    mocker.patch('qbosdk.apis.BillPayments.post', return_value=data['bill_payment_response'])
    workspace_id = 3

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    bill_payment, bill_payment_lineitems = create_bill_payment

    created_bill_payment = qbo_connection.post_bill_payment(bill_payment, bill_payment_lineitems)
    assert dict_compare_keys(created_bill_payment, data['bill_payment_response']) == [], 'construct bill payment api return diffs in keys'


def test_post_attachments(mocker, db):
    mocker.patch('qbosdk.apis.Attachments.post', return_value=[])
    workspace_id = 3

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    qbo_connection.post_attachments('asd', 'dfg', [{'download_url': 'sdfghj', 'name': 'ert', 'content_type': 'application/pdf'}])


def test_sync_dimensions_exception(db):
    workspace_id = 3

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    with mock.patch('fyle.platform.apis.v1.admin.expense_fields.list_all') as mock_call:
        mock_call.side_effect = NoPrivilegeError
        qbo_connection.sync_dimensions()

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.sync_accounts') as mock_call:
        mock_call.side_effect = Exception()
        qbo_connection.sync_dimensions()

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.sync_employees') as mock_call:
        mock_call.side_effect = Exception()
        qbo_connection.sync_dimensions()

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.sync_vendors') as mock_call:
        mock_call.side_effect = Exception()
        qbo_connection.sync_dimensions()

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.sync_customers') as mock_call:
        mock_call.side_effect = Exception()
        qbo_connection.sync_dimensions()

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.sync_classes') as mock_call:
        mock_call.side_effect = Exception()
        qbo_connection.sync_dimensions()

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.sync_departments') as mock_call:
        mock_call.side_effect = Exception()
        qbo_connection.sync_dimensions()

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.sync_tax_codes') as mock_call:
        mock_call.side_effect = Exception()
        qbo_connection.sync_dimensions()


def test_get_or_create_entity(mocker, db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(3)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=3)

    mocker.patch('qbosdk.apis.Vendors.post', return_value=data['post_vendor_resp'])
    mocker.patch('qbosdk.apis.Vendors.search_vendor_by_display_name', return_value=None)

    DestinationAttribute.objects.filter(workspace_id=3, attribute_type='VENDOR', value='Credit Card Misc').delete()

    # CCC expesnse with name Merchant
    expense_group = ExpenseGroup.objects.filter(fund_source='CCC', workspace_id = 3).first()
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workspace_general_settings.corporate_credit_card_expenses_object = 'JOURNAL ENTRY'
    workspace_general_settings.name_in_journal_entry = 'MERCHANT'
    workspace_general_settings.employee_field_mapping = 'VENDOR'
    workspace_general_settings.save()
    entity_ids = qbo_connection.get_or_create_entity(expense_group, workspace_general_settings)
    expenses = expense_group.expenses.all()
    for expense in expenses:
        assert entity_ids[expense.id] == data['post_vendor_resp']['Vendor']['Id']

    vendor_attributes = DestinationAttribute.objects.filter(attribute_type='VENDOR', workspace_id=3).last()
    vendor_attributes.value = 'Allison Hill'
    vendor_attributes.save()

    entity_ids = qbo_connection.get_or_create_entity(expense_group, workspace_general_settings)

    for expense in expenses:
        assert entity_ids[expense.id] == vendor_attributes.destination_id

    workspace_general_settings.auto_create_merchants_as_vendors = True
    workspace_general_settings.save()

    vendor_attributes.value = 'Joanna hill'
    vendor_attributes.save()

    entity_ids = qbo_connection.get_or_create_entity(expense_group, workspace_general_settings)

    for expense in expenses:
        assert entity_ids[expense.id] == data['post_vendor_resp']['Vendor']['Id']

    # CCC expesnse with name Employee
    workspace_general_settings.name_in_journal_entry = 'EMPLOYEE'
    workspace_general_settings.save()

    employee_attributes = EmployeeMapping.objects.filter(
        source_employee__value=expense_group.description.get('employee_email'),
        workspace_id=expense_group.workspace_id
    ).first()

    entity_ids = qbo_connection.get_or_create_entity(expense_group, workspace_general_settings)

    for expense in expenses:
        assert entity_ids[expense.id] == employee_attributes.destination_vendor.destination_id

    workspace_general_settings.import_vendors_as_merchants = True
    workspace_general_settings.employee_field_mapping = 'EMPLOYEE'
    workspace_general_settings.save()

    entity_ids = qbo_connection.get_or_create_entity(expense_group, workspace_general_settings)

    for expense in expenses:
        assert entity_ids[expense.id] == employee_attributes.destination_employee.destination_id

    # Personal expense
    expense_group = ExpenseGroup.objects.get(id=14)
    expenses = expense_group.expenses.all()
    employee_attributes = EmployeeMapping.objects.filter(
        source_employee__value=expense_group.description.get('employee_email'),
        workspace_id=expense_group.workspace_id
    ).first()

    entity_ids = qbo_connection.get_or_create_entity(expense_group, workspace_general_settings)

    for expense in expenses:
        assert entity_ids[expense.id] == employee_attributes.destination_employee.destination_id


def test_calculate_tax_amount(db):
    credentials_object = QBOCredential.objects.get(id=3)
    workspace_id = 3
    qbo_connector = QBOConnector(credentials_object, workspace_id)

    tax_rate_ref = {'taxRate': 10}
    total_tax_rate = 20
    line_tax_amount = 100

    expected_result = 50.0

    result = qbo_connector.calculate_tax_amount(tax_rate_ref, total_tax_rate, line_tax_amount)

    assert result == expected_result


def test_create_tax_detail(db):
    credentials_object = QBOCredential.objects.get(id=3)
    workspace_id = 3
    qbo_connector = QBOConnector(credentials_object, workspace_id)

    line = {
        'Amount': 100
    }

    tax_rate_ref = {
        'value': 'TAX123'
    }

    tax_amount = 10

    tax_detail = qbo_connector.create_tax_detail(line, tax_rate_ref, tax_amount)

    assert tax_detail == {
        'Amount': tax_amount,
        'DetailType': 'TaxLineDetail',
        "TaxLineDetail": {
            "TaxRateRef": {
                "value": tax_rate_ref['value']
            },
            "PercentBased": False,
            "NetAmountTaxable": round(line['Amount'], 2),
        }
    }


def test_update_existing_tax_detail(db):
    credentials_object = QBOCredential.objects.get(id=3)
    workspace_id = 3
    qbo_connector = QBOConnector(credentials_object, workspace_id)

    tax_detail = {
        'Amount': 100,
        'TaxLineDetail': {
            'TaxRateRef': {'value': '123'},
            "PercentBased": False,
            "NetAmountTaxable": 10,
        }
    }
    line = {'Amount': 50}
    tax_amount = 10

    updated_tax_detail = qbo_connector.update_existing_tax_detail(tax_detail, line, tax_amount)

    assert updated_tax_detail['Amount'] == 110
    assert updated_tax_detail['TaxLineDetail']['NetAmountTaxable'] == 60


def test_update_tax_details(db):
    credentials_object = QBOCredential.objects.get(id=3)
    workspace_id = 3
    qbo_connector = QBOConnector(credentials_object, workspace_id)

    tax_details = []
    line = {'Amount': 100, 'TaxAmount': 10}
    tax_rate_refs = [{'taxRate': 3, 'value': '1'}, {'taxRate': 2, 'value': '2'}]
    total_tax_rate = 5
    line_tax_amount = 100

    updated_tax_details = qbo_connector.update_tax_details(tax_details, line, tax_rate_refs, total_tax_rate, line_tax_amount)

    assert len(updated_tax_details) == 2
    assert updated_tax_details[0]['Amount'] == 60
    assert updated_tax_details[1]['Amount'] == 40


def test_get_override_tax_details(db, mocker):
    mocker.patch('fyle_accounting_mappings.models.DestinationAttribute.objects.filter')
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.update_tax_details')

    DestinationAttribute.objects.filter.return_value.first.return_value = mocker.Mock(detail={'tax_refs': [{'value': 'TAX_RATE_REF'}], 'tax_rate': 10})
    QBOConnector.update_tax_details.return_value = [{'Amount': 10, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': 'TAX_RATE_REF'}, 'PercentBased': False, 'NetAmountTaxable': 100}}]

    credentials_object = QBOCredential.objects.get(id=3)
    workspace_id = 3
    qbo_connector = QBOConnector(credentials_object, workspace_id)

    lines = [
        {
            'AccountBasedExpenseLineDetail': {
                'TaxCodeRef': {'value': 'TAX_CODE_ID'},
                'TaxAmount': 10.0
            }
        }
    ]

    tax_details = qbo_connector.get_override_tax_details(lines)

    # Assertions
    assert tax_details == [{'Amount': 10, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': 'TAX_RATE_REF'}, 'PercentBased': False, 'NetAmountTaxable': 100}}]


def test_skip_sync_attributes(mocker, db):
    mocker.patch(
        'qbosdk.apis.Classes.count',
        return_value=35000
    )
    mocker.patch(
        'qbosdk.apis.Accounts.count',
        return_value=35000
    )
    mocker.patch(
        'qbosdk.apis.Items.count',
        return_value=35000
    )
    mocker.patch(
        'qbosdk.apis.Departments.count',
        return_value=35000
    )
    mocker.patch(
        'qbosdk.apis.Customers.count',
        return_value=35000
    )
    mocker.patch(
        'qbosdk.apis.Vendors.count',
        return_value=35000
    )

    mocker.patch(
        'qbosdk.apis.TaxCodes.count',
        return_value=35000
    )

    today = timezone.now()
    Workspace.objects.filter(id=1).update(created_at=today)
    qbo_credentials = QBOCredential.get_active_qbo_credentials(1)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=1)

    Mapping.objects.filter(workspace_id=1).delete()
    CategoryMapping.objects.filter(workspace_id=1).delete()

    DestinationAttribute.objects.filter(workspace_id=1, attribute_type='CLASS').delete()

    qbo_connection.sync_classes()

    classifications = DestinationAttribute.objects.filter(attribute_type='CLASS', workspace_id=1).count()
    assert classifications == 0

    DestinationAttribute.objects.filter(workspace_id=1, attribute_type='ACCOUNT').delete()

    qbo_connection.sync_accounts()

    new_project_count = DestinationAttribute.objects.filter(workspace_id=1, attribute_type='ACCOUNT').count()
    assert new_project_count == 0

    DestinationAttribute.objects.filter(workspace_id=1, attribute_type='DEPARTMENT').delete()

    qbo_connection.sync_departments()

    new_project_count = DestinationAttribute.objects.filter(workspace_id=1, attribute_type='DEPARTMENT').count()
    assert new_project_count == 0

    DestinationAttribute.objects.filter(workspace_id=1, attribute_type='CUSTOMER').delete()

    qbo_connection.sync_customers()

    new_project_count = DestinationAttribute.objects.filter(workspace_id=1, attribute_type='CUSTOMER').count()
    assert new_project_count == 0

    DestinationAttribute.objects.filter(workspace_id=1, attribute_type='TAX_CODE').delete()

    qbo_connection.sync_tax_codes()

    new_project_count = DestinationAttribute.objects.filter(workspace_id=1, attribute_type='TAX_CODE').count()
    assert new_project_count == 0


def test_is_duplicate_deletion_skipped(db):
    # Create a dummy QBOCredential object
    qbo_credentials = QBOCredential.get_active_qbo_credentials(1)
    connector = QBOConnector(credentials_object=qbo_credentials, workspace_id=1)

    # These should return False
    for attr in ['ACCOUNT', 'VENDOR', 'ITEM', 'CUSTOMER', 'DEPARTMENT', 'CLASS']:
        assert connector.is_duplicate_deletion_skipped(attr) is False

    # These should return True (any attribute not in the above list)
    for attr in ['EMPLOYEE', 'TAX_CODE', 'SOMETHING_ELSE']:
        assert connector.is_duplicate_deletion_skipped(attr) is True


def test_is_import_enabled(db):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(1)
    connector = QBOConnector(credentials_object=qbo_credentials, workspace_id=1)

    # Clean up any previous settings
    MappingSetting.objects.filter(workspace_id=1).delete()

    # Mock pre_save and post_save signals for MappingSetting
    with mock.patch('django.db.models.signals.pre_save.send'), \
         mock.patch('django.db.models.signals.post_save.send'):

        # Create WorkspaceGeneralSettings with all import flags False
        WorkspaceGeneralSettings.objects.filter(workspace_id=1).update(
            workspace_id=1,
            import_categories=False,
            import_items=False,
            import_vendors_as_merchants=False
        )

        # ACCOUNT: import_categories False
        assert connector.is_import_enabled('ACCOUNT') is False
        # Set import_categories True
        WorkspaceGeneralSettings.objects.filter(workspace_id=1).update(import_categories=True)
        assert connector.is_import_enabled('ACCOUNT') is True

        # ITEM: import_items False
        WorkspaceGeneralSettings.objects.filter(workspace_id=1).update(import_items=False)
        assert connector.is_import_enabled('ITEM') is False
        # Set import_items True
        WorkspaceGeneralSettings.objects.filter(workspace_id=1).update(import_items=True)
        assert connector.is_import_enabled('ITEM') is True

        # VENDOR: import_vendors_as_merchants False
        WorkspaceGeneralSettings.objects.filter(workspace_id=1).update(import_vendors_as_merchants=False)
        assert connector.is_import_enabled('VENDOR') is False
        # Set import_vendors_as_merchants True
        WorkspaceGeneralSettings.objects.filter(workspace_id=1).update(import_vendors_as_merchants=True)
        assert connector.is_import_enabled('VENDOR') is True

        # CUSTOMER, DEPARTMENT, CLASS: MappingSetting.import_to_fyle False
        for attr in ['CUSTOMER', 'DEPARTMENT', 'CLASS']:
            MappingSetting.objects.filter(workspace_id=1, destination_field=attr).delete()
            # Create with import_to_fyle False
            MappingSetting.objects.create(
                workspace_id=1,
                destination_field=attr,
                source_field=attr,
                is_custom=False,
                import_to_fyle=False
            )
            assert connector.is_import_enabled(attr) is False
            # Now update to import_to_fyle True
            MappingSetting.objects.filter(workspace_id=1, destination_field=attr).update(import_to_fyle=True)
            assert connector.is_import_enabled(attr) is True

        # Negative case: unknown attribute_type
        assert connector.is_import_enabled('SOMETHING_ELSE') is False


def test_get_attribute_disable_callback_path(db, mocker):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(1)
    connector = QBOConnector(credentials_object=qbo_credentials, workspace_id=1)

    # Direct ACCOUNT and VENDOR
    assert connector.get_attribute_disable_callback_path('ACCOUNT') == 'fyle_integrations_imports.modules.categories.disable_categories'
    assert connector.get_attribute_disable_callback_path('VENDOR') == 'fyle_integrations_imports.modules.merchants.disable_merchants'

    # MappingSetting with is_custom False and known source_field
    with mock.patch('apps.quickbooks_online.utils.MappingSetting.objects.filter') as mock_filter:
        mock_instance = mock.Mock()
        mock_instance.is_custom = False
        mock_instance.source_field = 'PROJECT'
        mock_filter.return_value.first.return_value = mock_instance
        result = connector.get_attribute_disable_callback_path('CUSTOMER')
        assert result == 'fyle_integrations_imports.modules.projects.disable_projects'

    # MappingSetting with is_custom True (should return None)
    with mock.patch('apps.quickbooks_online.utils.MappingSetting.objects.filter') as mock_filter:
        mock_instance = mock.Mock()
        mock_instance.is_custom = True
        mock_filter.return_value.first.return_value = mock_instance
        result = connector.get_attribute_disable_callback_path('CUSTOMER')
        assert result is None

    # No MappingSetting found (should return None)
    with mock.patch('apps.quickbooks_online.utils.MappingSetting.objects.filter') as mock_filter:
        mock_filter.return_value.first.return_value = None
        result = connector.get_attribute_disable_callback_path('CUSTOMER')
        assert result is None


def test_is_sync_allowed(db):
    workspace_id = 3
    workspace = Workspace.objects.get(id=workspace_id)
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    assert qbo_connection.is_sync_allowed(attribute_count=15000) is True
    assert qbo_connection.is_sync_allowed(attribute_count=30000) is True

    workspace.created_at = timezone.make_aware(datetime(2024, 9, 15))
    workspace.save()
    assert qbo_connection.is_sync_allowed(attribute_count=35000) is True

    workspace.created_at = timezone.make_aware(datetime(2024, 10, 15))
    workspace.save()
    assert qbo_connection.is_sync_allowed(attribute_count=35000) is False


def test_sync_methods_persist_attribute_counts(mocker, db):
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    QBOAttributesCount.objects.get_or_create(workspace_id=workspace_id)

    mocker.patch('qbosdk.apis.Accounts.count', return_value=250)
    mocker.patch('qbosdk.apis.Accounts.get_all_generator', return_value=[data['account_response']])
    mocker.patch('qbosdk.apis.Accounts.get_inactive', return_value=[])
    qbo_connection.sync_accounts()

    qbo_count = QBOAttributesCount.objects.get(workspace_id=workspace_id)
    assert qbo_count.accounts_count == 250

    mocker.patch('qbosdk.apis.Items.count', return_value=150)
    mocker.patch('qbosdk.apis.Items.get_all_generator', return_value=[data['items_response']])
    mocker.patch('qbosdk.apis.Items.get_inactive', return_value=[])
    qbo_connection.sync_items()

    qbo_count.refresh_from_db()
    assert qbo_count.items_count == 150


def test_sync_skips_when_over_limit_new_workspace(mocker, db):
    workspace_id = 3
    workspace = Workspace.objects.get(id=workspace_id)
    workspace.created_at = timezone.make_aware(datetime(2024, 11, 1))
    workspace.save()

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    QBOAttributesCount.objects.get_or_create(workspace_id=workspace_id)

    mocker.patch('qbosdk.apis.Accounts.count', return_value=35000)
    mock_get_all = mocker.patch('qbosdk.apis.Accounts.get_all_generator')

    qbo_connection.sync_accounts()

    qbo_count = QBOAttributesCount.objects.get(workspace_id=workspace_id)
    assert qbo_count.accounts_count == 35000
    mock_get_all.assert_not_called()

    mocker.patch('qbosdk.apis.Items.count', return_value=35000)
    mock_items_get_all = mocker.patch('qbosdk.apis.Items.get_all_generator')

    qbo_connection.sync_items()

    qbo_count.refresh_from_db()
    assert qbo_count.items_count == 35000
    mock_items_get_all.assert_not_called()

    mocker.patch('qbosdk.apis.Vendors.count', return_value=35000)
    mock_vendors_get_all = mocker.patch('qbosdk.apis.Vendors.get_all_generator')

    qbo_connection.sync_vendors()

    qbo_count.refresh_from_db()
    assert qbo_count.vendors_count == 35000
    mock_vendors_get_all.assert_not_called()
