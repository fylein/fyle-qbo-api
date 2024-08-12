import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List

import unidecode
from django.conf import settings
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping
from qbosdk import QuickbooksOnlineSDK
from qbosdk.exceptions import WrongParamsError

from apps.fyle.models import ExpenseGroup
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.models import (
    Bill,
    BillLineitem,
    BillPayment,
    BillPaymentLineitem,
    Cheque,
    ChequeLineitem,
    CreditCardPurchase,
    CreditCardPurchaseLineitem,
    JournalEntry,
    JournalEntryLineitem,
    QBOExpense,
    QBOExpenseLineitem,
)
from apps.workspaces.models import QBOCredential, Workspace, WorkspaceGeneralSettings
from apps.workspaces.utils import round_amount
from fyle_integrations_imports.models import ImportLog

logger = logging.getLogger(__name__)
logger.level = logging.INFO

SYNC_UPPER_LIMIT = {'customers': 25000}


def format_special_characters(value: str) -> str:
    """
    Formats special characters in the string.
    :param value: string to be formatted
    :return: formatted string
    """
    formatted_string = unidecode.unidecode(u'{}'.format(value))
    if not formatted_string.strip():
        return ''

    return formatted_string


def get_last_synced_time(workspace_id: int, attribute_type: str):
    """
    Get the last synced time for the given attribute type
    :param workspace_id: workspace id
    :param attribute_type: attribute type
    :return: last synced time
    """
    import_log = ImportLog.objects.filter(
        workspace_id=workspace_id,
        attribute_type=attribute_type,
        status='COMPLETE'
    ).first()

    last_synced_time = None

    if import_log is not None and import_log.last_successful_run_at is not None:
        last_synced_time = import_log.last_successful_run_at
    else:
        last_synced_time = Workspace.objects.get(id=workspace_id).created_at

    last_synced_time_formatted = last_synced_time.strftime('%Y-%m-%dT%H:%M:%S-00:00')

    return last_synced_time_formatted


CHARTS_OF_ACCOUNTS = ['Expense', 'Other Expense', 'Fixed Asset', 'Cost of Goods Sold', 'Current Liability', 'Equity', 'Other Current Asset', 'Other Current Liability', 'Long Term Liability', 'Current Asset', 'Income', 'Other Income', 'Other Asset']


class QBOConnector:
    """
    QBO utility functions
    """

    def __init__(self, credentials_object: QBOCredential, workspace_id: int):
        client_id = settings.QBO_CLIENT_ID
        client_secret = settings.QBO_CLIENT_SECRET
        environment = settings.QBO_ENVIRONMENT
        refresh_token = credentials_object.refresh_token

        self.connection = QuickbooksOnlineSDK(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, realm_id=credentials_object.realm_id, environment=environment)

        self.workspace_id = workspace_id

        credentials_object.refresh_token = self.connection.refresh_token
        credentials_object.save()

    def get_or_create_vendor(self, vendor_name: str, email: str = None, create: bool = False):
        """
        Call qbo api to get or create vendor
        :param email: email for vendor user
        :param vendor_name: Name of the vendor
        :param create: False to just Get and True to Get or Create if not exists
        :return: Vendor
        """
        original_vendor_name = vendor_name
        vendor_name = vendor_name.replace("'", "\\'")  # Replacing ' with \\'
        vendor_name = vendor_name.replace('#', '%23')  # Replace '#' with %23
        vendor_name = vendor_name.replace('&', '%26')  # Replace '&' with %26

        vendor = self.connection.vendors.search_vendor_by_display_name(vendor_name)

        if not vendor:
            if create:
                # safe check to avoid duplicate vendor name exist error
                if DestinationAttribute.objects.filter(value=vendor_name, workspace_id=self.workspace_id).exists():
                    return
                created_vendor = self.post_vendor(original_vendor_name, email)
                return self.create_vendor_destionation_attribute(created_vendor)
            else:
                return
        else:
            return self.create_vendor_destionation_attribute(vendor)

    def get_effective_tax_rates(self, tax_rates):
        effective_tax_rate = 0
        tax_rate_refs = []
        for tax_rate in tax_rates:
            if 'TaxRateRef' in tax_rate:
                tax_rate_id = tax_rate['TaxRateRef']['value']
                tax_rate_by_id = self.connection.tax_rates.get_by_id(tax_rate_id)
                tax_rate['TaxRateRef']['taxRate'] = tax_rate_by_id['RateValue'] if 'RateValue' in tax_rate_by_id else 0
                tax_rate_refs.append(tax_rate['TaxRateRef'])

            if 'RateValue' in tax_rate_by_id:
                effective_tax_rate += tax_rate_by_id['RateValue']

        return effective_tax_rate, tax_rate_refs

    def get_tax_inclusive_amount(self, amount, default_tax_code_id):

        tax_attribute = DestinationAttribute.objects.filter(destination_id=default_tax_code_id, attribute_type='TAX_CODE', workspace_id=self.workspace_id).first()
        tax_inclusive_amount = amount
        if tax_attribute:
            tax_rate = float((tax_attribute.detail['tax_rate']) / 100)
            tax_amount = round_amount((amount - (amount / (tax_rate + 1))), 2)
            tax_inclusive_amount = round_amount((amount - tax_amount), 2)

        return tax_inclusive_amount

    def sync_items(self):
        """
        Get items
        """
        items_generator = self.connection.items.get_all_generator()
        general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()

        # For getting all the items, any inactive item will not be returned
        for items in items_generator:
            item_attributes = []
            for item in items:
                if item['Active']:
                    item_attributes.append({'attribute_type': 'ACCOUNT', 'display_name': 'Item', 'value': item['FullyQualifiedName'], 'destination_id': item['Id'], 'active': general_settings.import_items if general_settings else False})
            DestinationAttribute.bulk_create_or_update_destination_attributes(item_attributes, 'ACCOUNT', self.workspace_id, True, 'Item')

        last_synced_time = get_last_synced_time(self.workspace_id, 'CATEGORY')

        # get the inactive items generator
        inactive_items_generator = self.connection.items.get_inactive(last_synced_time)

        for inactive_items in inactive_items_generator:
            inactive_item_attributes = []
            for inactive_item in inactive_items:
                value = inactive_item['FullyQualifiedName'].replace(" (deleted)", "").rstrip()
                inactive_item_attributes.append({'attribute_type': 'ACCOUNT', 'display_name': 'Item', 'value': value, 'destination_id': inactive_item['Id'], 'active': False})
            DestinationAttribute.bulk_create_or_update_destination_attributes(inactive_item_attributes, 'ACCOUNT', self.workspace_id, True, 'Item')

        return []

    def sync_accounts(self):
        """
        Get accounts
        """
        accounts_generator = self.connection.accounts.get_all_generator()
        category_sync_version = 'v2'
        general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()
        if general_settings:
            category_sync_version = general_settings.category_sync_version

        for accounts in accounts_generator:
            account_attributes = {'account': [], 'credit_card_account': [], 'bank_account': [], 'accounts_payable': []}
            for account in accounts:
                value = format_special_characters(account['Name'] if category_sync_version == 'v1' else account['FullyQualifiedName'])

                if general_settings and account['AccountType'] in CHARTS_OF_ACCOUNTS and value:
                    account_attributes['account'].append(
                        {'attribute_type': 'ACCOUNT', 'display_name': 'Account', 'value': value, 'destination_id': account['Id'], 'active': True, 'detail': {'fully_qualified_name': account['FullyQualifiedName'], 'account_type': account['AccountType']}}
                    )

                elif account['AccountType'] == 'Credit Card' and value:
                    account_attributes['credit_card_account'].append(
                        {
                            'attribute_type': 'CREDIT_CARD_ACCOUNT',
                            'display_name': 'Credit Card Account',
                            'value': value,
                            'destination_id': account['Id'],
                            'active': account['Active'],
                            'detail': {'fully_qualified_name': account['FullyQualifiedName'], 'account_type': account['AccountType']},
                        }
                    )

                elif account['AccountType'] == 'Bank' and value:
                    account_attributes['bank_account'].append(
                        {
                            'attribute_type': 'BANK_ACCOUNT',
                            'display_name': 'Bank Account',
                            'value': value,
                            'destination_id': account['Id'],
                            'active': account['Active'],
                            'detail': {'fully_qualified_name': account['FullyQualifiedName'], 'account_type': account['AccountType']},
                        }
                    )

                elif account['AccountType'] == 'Accounts Payable' and value:
                    account_attributes['accounts_payable'].append(
                        {
                            'attribute_type': 'ACCOUNTS_PAYABLE',
                            'display_name': 'Accounts Payable',
                            'value': value,
                            'destination_id': account['Id'],
                            'active': account['Active'],
                            'detail': {'fully_qualified_name': account['FullyQualifiedName'], 'account_type': account['AccountType']},
                        }
                    )

            for attribute_type, attribute in account_attributes.items():
                if attribute:
                    DestinationAttribute.bulk_create_or_update_destination_attributes(attribute, attribute_type.upper(), self.workspace_id, True, attribute_type.title().replace('_', ' '))

        last_synced_time = get_last_synced_time(self.workspace_id, 'CATEGORY')

        # get the inactive accounts generator
        inactive_accounts_generator = self.connection.accounts.get_inactive(last_synced_time)

        for inactive_accounts in inactive_accounts_generator:
            inactive_account_attributes = {'account': []}
            for inactive_account in inactive_accounts:
                value = inactive_account['Name'].replace(" (deleted)", "").rstrip() if category_sync_version == 'v1' else inactive_account['FullyQualifiedName'].replace(" (deleted)", "").rstrip()
                full_qualified_name = inactive_account['FullyQualifiedName'].replace(" (deleted)", "").rstrip()
                inactive_account_attributes['account'].append(
                    {
                        'attribute_type': 'ACCOUNT',
                        'display_name': 'Account',
                        'value': value,
                        'destination_id': inactive_account['Id'],
                        'active': False,
                        'detail': {'fully_qualified_name': full_qualified_name, 'account_type': inactive_account['AccountType']},
                    }
                )

            for attribute_type, attribute in inactive_account_attributes.items():
                if attribute:
                    DestinationAttribute.bulk_create_or_update_destination_attributes(attribute, attribute_type.upper(), self.workspace_id, True, attribute_type.title().replace('_', ' '))

        return []

    def sync_departments(self):
        """
        Get departments
        """
        departments_generator = self.connection.departments.get_all_generator()

        for departments in departments_generator:
            department_attributes = []
            for department in departments:
                department_attributes.append({'attribute_type': 'DEPARTMENT', 'display_name': 'Department', 'value': department['FullyQualifiedName'], 'destination_id': department['Id'], 'active': department['Active']})

            DestinationAttribute.bulk_create_or_update_destination_attributes(department_attributes, 'DEPARTMENT', self.workspace_id, True)

        return []

    def sync_tax_codes(self):
        """
        Get Tax Codes
        """
        tax_codes_generator = self.connection.tax_codes.get_all_generator()

        for tax_codes in tax_codes_generator:
            tax_attributes = []
            for tax_code in tax_codes:
                if 'PurchaseTaxRateList' in tax_code.keys():
                    if tax_code['PurchaseTaxRateList']['TaxRateDetail']:
                        effective_tax_rate, tax_rates = self.get_effective_tax_rates(tax_code['PurchaseTaxRateList']['TaxRateDetail'])
                        if effective_tax_rate >= 0:
                            tax_attributes.append(
                                {
                                    'attribute_type': 'TAX_CODE',
                                    'display_name': 'Tax Code',
                                    'value': '{0} @{1}%'.format(tax_code['Name'], effective_tax_rate),
                                    'destination_id': tax_code['Id'],
                                    'active': True,
                                    'detail': {'tax_rate': effective_tax_rate, 'tax_refs': tax_rates},
                                }
                            )

            DestinationAttribute.bulk_create_or_update_destination_attributes(tax_attributes, 'TAX_CODE', self.workspace_id, True)

        return []

    def sync_vendors(self):
        """
        Get vendors
        """
        vendors_generator = self.connection.vendors.get_all_generator()

        for vendors in vendors_generator:
            vendor_attributes = []
            for vendor in vendors:
                if vendor['Active']:
                    detail = {
                        'email': vendor['PrimaryEmailAddr']['Address'] if ('PrimaryEmailAddr' in vendor and vendor['PrimaryEmailAddr'] and 'Address' in vendor['PrimaryEmailAddr'] and vendor['PrimaryEmailAddr']['Address']) else None,
                        'currency': vendor['CurrencyRef']['value'] if 'CurrencyRef' in vendor else None,
                    }
                    vendor_attributes.append({'attribute_type': 'VENDOR', 'display_name': 'vendor', 'value': vendor['DisplayName'], 'destination_id': vendor['Id'], 'detail': detail, 'active': vendor['Active']})

            DestinationAttribute.bulk_create_or_update_destination_attributes(vendor_attributes, 'VENDOR', self.workspace_id, True)

        last_synced_time = get_last_synced_time(self.workspace_id, 'MERCHANT')

        # get the inactive vendors generator
        inactive_vendors_generator = self.connection.vendors.get_inactive(last_synced_time)

        for inactive_vendors in inactive_vendors_generator:
            inactive_vendor_attributes = []
            for inactive_vendor in inactive_vendors:
                vendor_display_name = inactive_vendor['DisplayName'].replace(" (deleted)", "").rstrip()
                inactive_vendor_attributes.append({'attribute_type': 'VENDOR', 'display_name': 'vendor', 'value': vendor_display_name, 'destination_id': inactive_vendor['Id'], 'active': False})

            DestinationAttribute.bulk_create_or_update_destination_attributes(inactive_vendor_attributes, 'VENDOR', self.workspace_id, True)

        return []

    def create_vendor_destionation_attribute(self, vendor):
        created_vendor = DestinationAttribute.create_or_update_destination_attribute(
            {
                'attribute_type': 'VENDOR',
                'display_name': 'vendor',
                'value': vendor['DisplayName'],
                'destination_id': vendor['Id'],
                'active': vendor['Active'],
                'detail': {'email': vendor['PrimaryEmailAddr']['Address'] if 'PrimaryEmailAddr' in vendor else None},
            },
            self.workspace_id,
        )

        return created_vendor

    def post_vendor(self, vendor_name: str, email: str):
        """
        Create an Vendor on Quickbooks online
        :param email: email for employee vendors
        :param vendor_name: vendor attribute to be created
        :return: Vendor Desination Atribute
        """
        currency = Workspace.objects.get(id=self.workspace_id).fyle_currency

        vendor = {
            'GivenName': vendor_name.split(' ')[0] if email else None,
            'FamilyName': (vendor_name.split(' ')[-1] if len(vendor_name.split(' ')) > 1 else '') if email else None,
            'DisplayName': vendor_name,
            'PrimaryEmailAddr': {'Address': email},
            'CurrencyRef': {'value': currency},
        }
        created_vendor = self.connection.vendors.post(vendor)['Vendor']

        return created_vendor

    def sync_employees(self):
        """
        Get employees
        """
        employees_generator = self.connection.employees.get_all_generator()

        for employees in employees_generator:
            employee_attributes = []
            for employee in employees:
                detail = {'email': employee['PrimaryEmailAddr']['Address'] if ('PrimaryEmailAddr' in employee and employee['PrimaryEmailAddr'] and 'Address' in employee['PrimaryEmailAddr'] and employee['PrimaryEmailAddr']['Address']) else None}
                employee_attributes.append({'attribute_type': 'EMPLOYEE', 'display_name': 'employee', 'value': employee['DisplayName'], 'destination_id': employee['Id'], 'detail': detail, 'active': True})

            DestinationAttribute.bulk_create_or_update_destination_attributes(employee_attributes, 'EMPLOYEE', self.workspace_id, True)

        return []

    def sync_classes(self):
        """
        Get classes
        """
        classes_generator = self.connection.classes.get_all_generator()

        for classes in classes_generator:
            class_attributes = []
            for qbo_class in classes:
                class_attributes.append({'attribute_type': 'CLASS', 'display_name': 'class', 'value': qbo_class['FullyQualifiedName'], 'destination_id': qbo_class['Id'], 'active': qbo_class['Active']})

            DestinationAttribute.bulk_create_or_update_destination_attributes(class_attributes, 'CLASS', self.workspace_id, True)

        return []

    def sync_customers(self):
        """
        Get customers
        """
        customers_count = self.connection.customers.count()
        if customers_count < SYNC_UPPER_LIMIT['customers']:
            customers_generator = self.connection.customers.get_all_generator()

            for customers in customers_generator:
                customer_attributes = []
                for customer in customers:
                    value = format_special_characters(customer['FullyQualifiedName'])
                    if customer['Active'] and value:
                        customer_attributes.append({'attribute_type': 'CUSTOMER', 'display_name': 'customer', 'value': value, 'destination_id': customer['Id'], 'active': True})

                DestinationAttribute.bulk_create_or_update_destination_attributes(customer_attributes, 'CUSTOMER', self.workspace_id, True)

            last_synced_time = get_last_synced_time(self.workspace_id, 'PROJECT')

            # get the inactive customers generator
            inactive_customers_generator = self.connection.customers.get_inactive(last_synced_time)

            for inactive_customers in inactive_customers_generator:
                inactive_customer_attributes = []
                for inactive_customer in inactive_customers:
                    display_name = inactive_customer['DisplayName'].replace(" (deleted)", "").rstrip()
                    inactive_customer_attributes.append({'attribute_type': 'CUSTOMER', 'display_name': 'customer', 'value': display_name, 'destination_id': inactive_customer['Id'], 'active': False})

                DestinationAttribute.bulk_create_or_update_destination_attributes(inactive_customer_attributes, 'CUSTOMER', self.workspace_id, True)

        return []

    def sync_dimensions(self):

        try:
            self.sync_accounts()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_employees()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_vendors()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_customers()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_classes()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_tax_codes()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_departments()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_items()
        except Exception as exception:
            logger.info(exception)

    def calculate_tax_amount(self, tax_rate_ref, total_tax_rate, line_tax_amount):
        """
        Calculate the tax amount for a given tax rate reference.

        Args:
            tax_rate_ref (dict): Reference to a specific tax rate, e.g., {'value': '1', 'taxRate': 10.0}
            total_tax_rate (float): The total tax rate applicable, e.g., 15.0
            line_tax_amount (float): The total tax amount for the line, e.g., 50.0

        Returns:
            float: Calculated tax amount, rounded to 2 decimal places.
        """
        # If total tax rate is zero, return zero to avoid division by zero error
        if total_tax_rate == 0:
            return 0
        # Calculate the tax amount for the specific tax rate
        return round_amount((line_tax_amount * (tax_rate_ref['taxRate'] / total_tax_rate)), 2)

    def create_tax_detail(self, line, tax_rate_ref, tax_amount):
        """
        Create a new tax detail entry.

        Args:
            line (dict): Line item data, e.g., {'Amount': 100.0}
            tax_rate_ref (dict): Reference to a specific tax rate, e.g., {'value': '1', 'taxRate': 10.0}
            tax_amount (float): Calculated tax amount, e.g., 5.0

        Returns:
            dict: A dictionary representing the tax detail.
        """
        return {
            'Amount': tax_amount,
            'DetailType': 'TaxLineDetail',
            "TaxLineDetail": {
                "TaxRateRef": {
                    "value": tax_rate_ref['value']
                },
                "PercentBased": False,
                "NetAmountTaxable": round_amount(line['Amount'], 2),
            }
        }

    def update_existing_tax_detail(self, tax_detail, line, tax_amount):
        """
        Update an existing tax detail entry with additional tax amount.

        Args:
            tax_detail (dict): Existing tax detail entry.
            line (dict): Line item data, e.g., {'Amount': 100.0}
            tax_amount (float): Additional tax amount to add, e.g., 5.0

        Returns:
            dict: Updated tax detail entry.
        """
        # Add the new tax amount to the existing amount
        tax_detail['Amount'] = tax_detail['Amount'] + tax_amount
        # Round the updated amount to 2 decimal places
        tax_detail['Amount'] = round_amount(tax_detail['Amount'], 2)
        # Update the net amount taxable
        tax_detail['TaxLineDetail']['NetAmountTaxable'] += line['Amount']
        return tax_detail

    def update_tax_details(self, tax_details, line, tax_rate_refs, total_tax_rate, line_tax_amount):
        """
        Update the list of tax details with new tax amounts.

        Args:
            tax_details (list): List of existing tax detail entries.
            line (dict): Line item data, e.g., {'Amount': 100.0}
            tax_rate_refs (list): List of tax rate references, e.g., [{'value': '1', 'taxRate': 10.0}]
            total_tax_rate (float): The total tax rate applicable, e.g., 15.0
            line_tax_amount (float): The total tax amount for the line, e.g., 50.0

        Returns:
            list: Updated list of tax detail entries.
        """
        updated_tax_details = tax_details[:]

        for tax_rate_ref in tax_rate_refs:
            tax_amount = self.calculate_tax_amount(tax_rate_ref, total_tax_rate, line_tax_amount)
            tax_amount = round_amount(tax_amount, 2)
            updated = False

            # Check if the tax detail already exists
            for i, tax_detail in enumerate(updated_tax_details):
                if tax_rate_ref['value'] == tax_detail['TaxLineDetail']['TaxRateRef']['value']:
                    updated_tax_details[i] = self.update_existing_tax_detail(tax_detail, line, tax_amount)
                    updated = True
                    break

            if not updated:
                # If the tax detail does not exist, create a new one
                updated_tax_details.append(self.create_tax_detail(line, tax_rate_ref, tax_amount))

        return updated_tax_details

    def get_override_tax_details(self, lines, is_journal_entry_export: bool = False):
        """
        Get the overridden tax details for a list of lines.

        Args:
            lines (list): List of line items.
            is_journal_entry_export (bool): Flag to filter lines for journal entry export. Default is False.

        Returns:
            list: List of tax detail entries.
        """
        if is_journal_entry_export:
            lines = [line for line in lines if line.get('JournalEntryLineDetail', {}).get('PostingType') == 'Debit']

        tax_details = []
        for line in lines:
            if is_journal_entry_export:
                line_details = line.get('JournalEntryLineDetail', {})
            else:
                # Get line details for account-based or item-based expense line
                line_details = line.get('AccountBasedExpenseLineDetail', {}) if 'AccountBasedExpenseLineDetail' in line else line.get('ItemBasedExpenseLineDetail', {})

            tax_code_ref = line_details.get('TaxCodeRef')

            if tax_code_ref:
                tax_code = DestinationAttribute.objects.filter(
                    destination_id=tax_code_ref.get('value'),
                    attribute_type='TAX_CODE',
                    workspace_id=self.workspace_id
                ).first()

                if not tax_code:
                    continue

                tax_rate_refs = tax_code.detail.get('tax_refs', [])
                total_tax_rate = tax_code.detail.get('tax_rate', 0)
                line_tax_amount = line_details.get('TaxAmount', 0)
                tax_details = self.update_tax_details(tax_details, line, tax_rate_refs, total_tax_rate, line_tax_amount)

        return tax_details

    def purchase_object_payload(self, purchase_object, line, payment_type, account_ref, doc_number: str = None, credit=None):
        general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()

        purchase_object_payload = {
            'DocNumber': doc_number if doc_number else None,
            'PaymentType': payment_type,
            'AccountRef': {'value': account_ref},
            'EntityRef': {'value': purchase_object.entity_id},
            'DepartmentRef': {'value': purchase_object.department_id},
            'TxnDate': purchase_object.transaction_date,
            'CurrencyRef': {'value': purchase_object.currency},
            'PrivateNote': purchase_object.private_note,
            'Credit': credit,
            'Line': line,
        }

        if general_settings.import_tax_codes:
            if general_settings.is_tax_override_enabled:
                tax_details = self.get_override_tax_details(line)
                purchase_object_payload.update({'GlobalTaxCalculation': 'TaxExcluded', 'TxnTaxDetail': {"TaxLine": tax_details}})
            else:
                purchase_object_payload.update({'GlobalTaxCalculation': 'TaxInclusive'})

        [line['ItemBasedExpenseLineDetail'].pop('TaxAmount') for line in purchase_object_payload['Line'] if 'ItemBasedExpenseLineDetail' in line]

        return purchase_object_payload

    def __construct_bill_lineitems(self, bill_lineitems: List[BillLineitem], general_mappings: GeneralMapping) -> List[Dict]:
        """
        Create bill line items
        :param bill_lineitems: list of bill line items extracted from database
        :return: constructed line items
        """
        lines = []

        for line in bill_lineitems:
            lineitem = {
                'Description': line.description,
                'DetailType': line.detail_type,
                'Amount': line.amount - line.tax_amount if (line.tax_code and line.tax_amount is not None) else self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id),
                line.detail_type: {
                    'CustomerRef': {'value': line.customer_id},
                    'ClassRef': {'value': line.class_id},
                    'TaxCodeRef': {'value': line.tax_code if (line.tax_code and line.tax_amount is not None) else general_mappings.default_tax_code_id},
                    'BillableStatus': 'Billable' if line.billable and line.customer_id else 'NotBillable',
                },
            }

            if line.detail_type == 'ItemBasedExpenseLineDetail':
                lineitem['ItemBasedExpenseLineDetail'].update({'ItemRef': {'value': line.item_id}, 'Qty': 1})
                lineitem['ItemBasedExpenseLineDetail'].update({'TaxAmount': line.tax_amount if (line.tax_code and line.tax_amount is not None) else round_amount(line.amount - self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id), 2)})
            else:
                lineitem['AccountBasedExpenseLineDetail'].update(
                    {
                        'AccountRef': {'value': line.account_id},
                        'TaxAmount': line.tax_amount if (line.tax_code and line.tax_amount is not None) else round_amount(line.amount - self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id), 2),
                    }
                )

            lines.append(lineitem)

        return lines

    def __construct_bill(self, bill: Bill, bill_lineitems: List[BillLineitem]) -> Dict:
        """
        Create a bill
        :param bill: bill object extracted from database
        :return: constructed bill
        """

        general_mappings = GeneralMapping.objects.filter(workspace_id=self.workspace_id).first()
        general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()
        qbo_home_currency = QBOCredential.objects.get(workspace_id=self.workspace_id).currency
        fyle_home_currency = bill.currency

        lines = self.__construct_bill_lineitems(bill_lineitems, general_mappings)

        bill_payload = {
            'VendorRef': {'value': bill.vendor_id},
            'APAccountRef': {'value': bill.accounts_payable_id},
            'DepartmentRef': {'value': bill.department_id},
            'TxnDate': bill.transaction_date,
            'CurrencyRef': {'value': bill.currency},
            'PrivateNote': bill.private_note,
            'Line': lines,
        }

        if general_settings.is_multi_currency_allowed and fyle_home_currency != qbo_home_currency and qbo_home_currency:
            exchange_rate = self.connection.exchange_rates.get_by_source(source_currency_code=fyle_home_currency)
            bill_payload['ExchangeRate'] = exchange_rate['Rate'] if "Rate" in exchange_rate else 1

            bill.exchange_rate = bill_payload['ExchangeRate']
            bill.save(update_fields=['exchange_rate'])

        if general_settings.import_tax_codes:
            if general_settings.is_tax_override_enabled:
                tax_details = self.get_override_tax_details(lines)
                bill_payload.update({'GlobalTaxCalculation': 'TaxExcluded', 'TxnTaxDetail': {"TaxLine": tax_details}})
            else:
                bill_payload.update({'GlobalTaxCalculation': 'TaxInclusive'})

        [line['ItemBasedExpenseLineDetail'].pop('TaxAmount') for line in bill_payload['Line'] if 'ItemBasedExpenseLineDetail' in line]

        logger.info("| Payload for Bill creation | Content: {{WORKSPACE_ID: {} EXPENSE_GROUP_ID: {} BILL_PAYLOAD: {}}}".format(self.workspace_id, bill.expense_group.id, bill_payload))
        return bill_payload

    def post_bill(self, bill: Bill, bill_lineitems: List[BillLineitem]):
        """
        Post bills to QBO
        """
        try:
            bills_payload = self.__construct_bill(bill, bill_lineitems)
            created_bill = self.connection.bills.post(bills_payload)
            return created_bill

        except WrongParamsError as bad_request:
            general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()

            response = json.loads(bad_request.response)
            if 'Fault' in response:
                error_response = response['Fault']['Error'][0]

                if general_settings.change_accounting_period and 'account period closed' in error_response['Message'].lower():
                    book_closed_date = self.connection.preferences.get()['AccountingInfoPrefs']['BookCloseDate']
                    txn_date = datetime.strptime(book_closed_date, '%Y-%m-%d') + timedelta(days=1)

                    bills_payload['TxnDate'] = txn_date.strftime("%Y-%m-%d")
                    created_bill = self.connection.bills.post(bills_payload)

                    bill.transaction_date = txn_date
                    bill.save()
                    return created_bill

            raise

    def get_bill(self, bill_id):
        """
        GET bill from QBO
        """
        bill = self.connection.bills.get_by_id(bill_id)
        return bill

    def __construct_qbo_expense_lineitems(self, qbo_expense_lineitems: List[QBOExpenseLineitem], general_mappings) -> List[Dict]:
        """
        Create Expense line items
        :param qbo_expense_lineitems: list of expense line items extracted from database
        :return: constructed line items
        """
        lines = []

        for line in qbo_expense_lineitems:
            lineitem = {
                'Description': line.description,
                'DetailType': line.detail_type,
                'Amount': line.amount - line.tax_amount if (line.tax_code and line.tax_amount is not None) else self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id),
                line.detail_type: {
                    'CustomerRef': {'value': line.customer_id},
                    'ClassRef': {'value': line.class_id},
                    'TaxCodeRef': {'value': line.tax_code if (line.tax_code and line.tax_amount is not None) else general_mappings.default_tax_code_id},
                    'BillableStatus': 'Billable' if line.billable and line.customer_id else 'NotBillable',
                },
            }

            if line.detail_type == 'ItemBasedExpenseLineDetail':
                lineitem['ItemBasedExpenseLineDetail'].update({'ItemRef': {'value': line.item_id}, 'Qty': 1})
                lineitem['ItemBasedExpenseLineDetail'].update({'TaxAmount': line.tax_amount if (line.tax_code and line.tax_amount is not None) else round_amount(line.amount - self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id), 2)})
            else:
                lineitem['AccountBasedExpenseLineDetail'].update(
                    {
                        'AccountRef': {'value': line.account_id},
                        'TaxAmount': line.tax_amount if (line.tax_code and line.tax_amount is not None) else round_amount(line.amount - self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id), 2),
                    }
                )

            lines.append(lineitem)

        return lines

    def __construct_qbo_expense(self, qbo_expense: QBOExpense, qbo_expense_lineitems: List[QBOExpenseLineitem]) -> Dict:
        """
        Create a expense
        :param qbo_expense: expense object extracted from database
        :return: constructed expense
        """
        general_mappings = GeneralMapping.objects.filter(workspace_id=self.workspace_id).first()

        line = self.__construct_qbo_expense_lineitems(qbo_expense_lineitems, general_mappings)
        qbo_expense_payload = self.purchase_object_payload(qbo_expense, line, account_ref=qbo_expense.expense_account_id, payment_type='Cash')

        logger.info("| Payload for Expense creation | Content: {{WORKSPACE_ID: {} EXPENSE_GROUP_ID: {} EXPENSE_PAYLOAD: {}}}".format(self.workspace_id, qbo_expense.expense_group.id, qbo_expense_payload))
        return qbo_expense_payload

    def post_qbo_expense(self, qbo_expense: QBOExpense, qbo_expense_lineitems: List[QBOExpenseLineitem]):
        """
        Post Expense to QBO
        """
        try:
            qbo_expenses_payload = self.__construct_qbo_expense(qbo_expense, qbo_expense_lineitems)
            created_qbo_expense = self.connection.purchases.post(qbo_expenses_payload)
            return created_qbo_expense

        except WrongParamsError as bad_request:
            general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()
            response = json.loads(bad_request.response)
            if 'Fault' in response:
                error_response = response['Fault']['Error'][0]

                if general_settings.change_accounting_period and 'account period closed' in error_response['Message'].lower():
                    book_closed_date = self.connection.preferences.get()['AccountingInfoPrefs']['BookCloseDate']
                    txn_date = datetime.strptime(book_closed_date, '%Y-%m-%d') + timedelta(days=1)
                    qbo_expenses_payload['TxnDate'] = txn_date.strftime("%Y-%m-%d")
                    created_qbo_expense = self.connection.purchases.post(qbo_expenses_payload)

                    qbo_expense.transaction_date = txn_date
                    qbo_expense.save()
                    return created_qbo_expense

            raise

    def __construct_cheque_lineitems(self, cheque_lineitems: List[ChequeLineitem], general_mappings: GeneralMapping) -> List[Dict]:
        """
        Create cheque lineitems
        :param cheque_lineitems: list of cheque line items extracted from database
        :return: constructed line items
        """
        lines = []
        for line in cheque_lineitems:
            lineitem = {
                'Description': line.description,
                'DetailType': line.detail_type,
                'Amount': line.amount - line.tax_amount if (line.tax_code and line.tax_amount is not None) else self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id),
                line.detail_type: {
                    'CustomerRef': {'value': line.customer_id},
                    'ClassRef': {'value': line.class_id},
                    'TaxCodeRef': {'value': line.tax_code if (line.tax_code and line.tax_amount is not None) else general_mappings.default_tax_code_id},
                    'BillableStatus': 'Billable' if line.billable and line.customer_id else 'NotBillable',
                },
            }

            if line.detail_type == 'ItemBasedExpenseLineDetail':
                lineitem['ItemBasedExpenseLineDetail'].update({'ItemRef': {'value': line.item_id}, 'Qty': 1})
                lineitem['ItemBasedExpenseLineDetail'].update({'TaxAmount': line.tax_amount if (line.tax_code and line.tax_amount is not None) else round_amount(line.amount - self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id), 2)})
            else:
                lineitem['AccountBasedExpenseLineDetail'].update(
                    {
                        'AccountRef': {'value': line.account_id},
                        'TaxAmount': line.tax_amount if (line.tax_code and line.tax_amount is not None) else round_amount(line.amount - self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id), 2),
                    }
                )

            lines.append(lineitem)

        return lines

    def __construct_cheque(self, cheque: Cheque, cheque_lineitems: List[ChequeLineitem]) -> Dict:
        """
        Create a cheque
        :param cheque: cheque object extracted from database
        :return: constructed cheque
        """
        general_mappings = GeneralMapping.objects.filter(workspace_id=self.workspace_id).first()

        line = self.__construct_cheque_lineitems(cheque_lineitems, general_mappings)
        cheque_payload = self.purchase_object_payload(cheque, line, account_ref=cheque.bank_account_id, payment_type='Check')

        logger.info("| Payload for Cheque creation | Content: {{WORKSPACE_ID: {} EXPENSE_GROUP_ID: {} CHEQUE_PAYLOAD: {}}}".format(self.workspace_id, cheque.expense_group.id, cheque_payload))
        return cheque_payload

    def post_cheque(self, cheque: Cheque, cheque_lineitems: List[ChequeLineitem]):
        """
        Post cheque to QBO
        """
        try:
            cheques_payload = self.__construct_cheque(cheque, cheque_lineitems)
            created_cheque = self.connection.purchases.post(cheques_payload)
            return created_cheque

        except WrongParamsError as bad_request:
            general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()
            response = json.loads(bad_request.response)
            if 'Fault' in response:
                error_response = json.loads(bad_request.response)['Fault']['Error'][0]

                if general_settings.change_accounting_period and 'account period closed' in error_response['Message'].lower():
                    book_closed_date = self.connection.preferences.get()['AccountingInfoPrefs']['BookCloseDate']
                    txn_date = datetime.strptime(book_closed_date, '%Y-%m-%d') + timedelta(days=1)
                    cheques_payload['TxnDate'] = txn_date.strftime("%Y-%m-%d")
                    created_cheque = self.connection.purchases.post(cheques_payload)

                    cheque.transaction_date = txn_date
                    cheque.save()
                    return created_cheque

            raise

    def __construct_credit_card_purchase_lineitems(self, credit_card_purchase_lineitems: List[CreditCardPurchaseLineitem], general_mappings: GeneralMapping) -> List[Dict]:
        """
        Create credit_card_purchase line items
        :param credit_card_purchase_lineitems: list of credit_card_purchase line items extracted from database
        :return: constructed line items
        """
        lines = []

        for line in credit_card_purchase_lineitems:
            lineitem = {
                'Description': line.description,
                'DetailType': line.detail_type,
                'Amount': line.amount - line.tax_amount if (line.tax_code and line.tax_amount is not None) else self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id),
                line.detail_type: {
                    'CustomerRef': {'value': line.customer_id},
                    'ClassRef': {'value': line.class_id},
                    'TaxCodeRef': {'value': line.tax_code if (line.tax_code and line.tax_amount is not None) else general_mappings.default_tax_code_id},
                    'BillableStatus': 'Billable' if line.billable and line.customer_id else 'NotBillable',
                },
            }

            if line.detail_type == 'ItemBasedExpenseLineDetail':
                lineitem['ItemBasedExpenseLineDetail'].update({'ItemRef': {'value': line.item_id}, 'Qty': 1})
                lineitem['ItemBasedExpenseLineDetail'].update({'TaxAmount': line.tax_amount if (line.tax_code and line.tax_amount is not None) else round_amount(line.amount - self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id), 2)})
            else:
                lineitem['AccountBasedExpenseLineDetail'].update(
                    {
                        'AccountRef': {'value': line.account_id},
                        'TaxAmount': line.tax_amount if (line.tax_code and line.tax_amount is not None) else round_amount(line.amount - self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id), 2),
                    }
                )

            lines.append(lineitem)

        return lines

    def __construct_credit_card_purchase(self, credit_card_purchase: CreditCardPurchase, credit_card_purchase_lineitems: List[CreditCardPurchaseLineitem]) -> Dict:
        """
        Create a credit_card_purchase
        :param credit_card_purchase: credit_card_purchase object extracted from database
        :return: constructed credit_card_purchase
        """
        general_mappings = GeneralMapping.objects.filter(workspace_id=self.workspace_id).first()

        line = self.__construct_credit_card_purchase_lineitems(credit_card_purchase_lineitems, general_mappings)
        credit = False

        for i in range(len(line)):
            if line[i]['Amount'] < 0:
                credit = True
                tax_amount = line[i][credit_card_purchase_lineitems[i].detail_type]['TaxAmount']
                line[i]['Amount'] = abs(line[i]['Amount'])
                line[i][credit_card_purchase_lineitems[i].detail_type]['TaxAmount'] = abs(tax_amount) if tax_amount else None

        credit_card_purchase_payload = self.purchase_object_payload(credit_card_purchase, line, account_ref=credit_card_purchase.ccc_account_id, payment_type='CreditCard', doc_number=credit_card_purchase.credit_card_purchase_number, credit=credit)

        logger.info("| Payload for Credit Card Purchase creation | Content: {{WORKSPACE_ID: {} EXPENSE_GROUP_ID: {} CREDIT_CARD_PURCHASE_PAYLOAD: {}}}".format(self.workspace_id, credit_card_purchase.expense_group.id, credit_card_purchase_payload))
        return credit_card_purchase_payload

    def post_credit_card_purchase(self, credit_card_purchase: CreditCardPurchase, credit_card_purchase_lineitems: List[CreditCardPurchaseLineitem]):

        """
        Post Credit Card Purchase  to QBO
        """
        try:
            credit_card_purchase_payload = self.__construct_credit_card_purchase(credit_card_purchase, credit_card_purchase_lineitems)
            created_credit_card_purchase = self.connection.purchases.post(credit_card_purchase_payload)
            return created_credit_card_purchase

        except WrongParamsError as bad_request:
            general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()
            response = json.loads(bad_request.response)
            if 'Fault' in response:
                error_response = json.loads(bad_request.response)['Fault']['Error'][0]

                if general_settings.change_accounting_period and 'account period closed' in error_response['Message'].lower():
                    book_closed_date = self.connection.preferences.get()['AccountingInfoPrefs']['BookCloseDate']
                    txn_date = datetime.strptime(book_closed_date, '%Y-%m-%d') + timedelta(days=1)
                    credit_card_purchase_payload['TxnDate'] = txn_date.strftime("%Y-%m-%d")
                    created_credit_card_purchase = self.connection.purchases.post(credit_card_purchase_payload)

                    credit_card_purchase.transaction_date = txn_date
                    credit_card_purchase.save()
                    return created_credit_card_purchase

            raise

    def _get_total_tax(self, lineitem, general_mappings):
        total_tax = 0
        if lineitem.tax_code and lineitem.tax_amount is not None:
            total_tax += lineitem.tax_amount
        else:
            total_tax += round_amount(lineitem.amount - self.get_tax_inclusive_amount(lineitem.amount, general_mappings.default_tax_code_id), 2)
        return total_tax

    def __group_journal_entry_credits(self, journal_entry_lineitems: List[JournalEntryLineitem], general_mappings: GeneralMapping) -> List[Dict]:
        card_objects = {}
        data = []

        configuration = WorkspaceGeneralSettings.objects.get(workspace_id=self.workspace_id)
        for lineitem in journal_entry_lineitems:
            tax_code = lineitem.tax_code if lineitem.tax_code else general_mappings.default_tax_code_id if (configuration.import_tax_codes and not lineitem.tax_code) else ""
            total_tax = self._get_total_tax(lineitem, general_mappings)
            if (lineitem.debit_account_id + tax_code) in card_objects:
                card_objects[lineitem.debit_account_id + tax_code]['amount'] = card_objects[lineitem.debit_account_id + tax_code]['amount'] + lineitem.amount
                card_objects[lineitem.debit_account_id + tax_code]['total_tax'] = card_objects[lineitem.debit_account_id + tax_code]['total_tax'] + self._get_total_tax(lineitem, general_mappings)
            else:
                card_objects[lineitem.debit_account_id + tax_code] = {
                    'debit_account_id': lineitem.debit_account_id,
                    'amount': lineitem.amount,
                    'entity_id': lineitem.entity_id,
                    'entity_type': lineitem.entity_type,
                    'tax_code': tax_code,
                    'total_tax': total_tax,
                }

        for key, value in card_objects.items():
            data.append(value)

        line_items = []
        for line in data:
            line_items.append(
                {
                    'DetailType': 'JournalEntryLineDetail',
                    'Description': 'Total Amount',
                    'Amount': line['amount'] - line['total_tax'],
                    'JournalEntryLineDetail': {
                        'PostingType': 'Credit',
                        'AccountRef': {'value': line['debit_account_id']},
                        'DepartmentRef': {'value': None},
                        'ClassRef': {'value': None},
                        'Entity': {'EntityRef': {'value': line['entity_id']}, 'Type': line['entity_type']},
                        'TaxCodeRef': {'value': line['tax_code'] if line['tax_code'] else general_mappings.default_tax_code_id},
                        'TaxInclusiveAmt': line['amount'],
                        "TaxApplicableOn": "Purchase",
                        'TaxAmount': line['total_tax'],
                    },
                }
            )
        return line_items

    def __construct_journal_entry_lineitems(self, journal_entry_lineitems: List[JournalEntryLineitem], posting_type, general_mappings: GeneralMapping, single_credit_line: bool = False) -> List[Dict]:
        """
        Create journal_entry line items
        :param journal_entry_lineitems: list of journal entry line items extracted from database
        :return: constructed line items
        """
        lines = []
        lineitems = journal_entry_lineitems
        if single_credit_line:
            non_refund_journal_entry_lineitems = []
            refund_journal_entry_lineitems = []
            for line in journal_entry_lineitems:
                if line.amount > 0:
                    non_refund_journal_entry_lineitems.append(line)
                else:
                    refund_journal_entry_lineitems.append(line)

            if non_refund_journal_entry_lineitems:
                single_credit_lines = self.__group_journal_entry_credits(non_refund_journal_entry_lineitems, general_mappings)
                for line in single_credit_lines:
                    lines.append(line)

            if refund_journal_entry_lineitems:
                lineitems = refund_journal_entry_lineitems
            else:
                return lines

        refund = False
        for line in lineitems:
            account_ref = None
            if line.amount < 0:
                refund = True

            if posting_type == 'Debit':
                account_ref = line.account_id
            if posting_type == 'Credit':
                account_ref = line.debit_account_id
            if posting_type == 'Debit' and refund:
                account_ref = line.debit_account_id
            if posting_type == 'Credit' and refund:
                account_ref = line.account_id

            final_amount = 0
            if line.tax_code and line.tax_amount is not None:
                final_amount = abs(line.amount) - abs(line.tax_amount)
            else:
                final_amount = abs(self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id))

            lineitem = {
                'DetailType': 'JournalEntryLineDetail',
                'Description': line.description,
                'Amount': round_amount(final_amount, 2),
                'JournalEntryLineDetail': {
                    'PostingType': posting_type,
                    'AccountRef': {'value': account_ref},
                    'DepartmentRef': {'value': line.department_id},
                    'ClassRef': {'value': line.class_id},
                    'Entity': {'EntityRef': {'value': line.entity_id}, 'Type': line.entity_type},
                    'TaxInclusiveAmt': round_amount(abs(line.amount), 2),
                    'TaxCodeRef': {'value': line.tax_code if (line.tax_code and line.tax_amount is not None) else general_mappings.default_tax_code_id},
                    'TaxAmount': abs(line.tax_amount if (line.tax_code and line.tax_amount is not None) else round_amount(line.amount - self.get_tax_inclusive_amount(line.amount, general_mappings.default_tax_code_id), 2)),
                    "TaxApplicableOn": "Purchase",
                },
            }
            lines.append(lineitem)
            refund = False

        return lines

    def __construct_journal_entry(self, journal_entry: JournalEntry, journal_entry_lineitems: List[JournalEntryLineitem], single_credit_line: bool) -> Dict:
        """
        Create a journal_entry
        :param journal_entry: journal_entry object extracted from database
        :return: constructed journal_entry
        """
        general_mappings = GeneralMapping.objects.filter(workspace_id=self.workspace_id).first()
        general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()

        tax_rate_refs = []

        credit_line = self.__construct_journal_entry_lineitems(journal_entry_lineitems, 'Credit', general_mappings, single_credit_line)
        debit_line = self.__construct_journal_entry_lineitems(journal_entry_lineitems, 'Debit', general_mappings)
        lines = []
        lines.extend(credit_line)
        lines.extend(debit_line)

        journal_entry_payload = {'TxnDate': journal_entry.transaction_date, 'PrivateNote': journal_entry.private_note, 'Line': lines, 'CurrencyRef': {"value": journal_entry.currency}, 'TxnTaxDetail': {'TaxLine': []}}

        if general_settings.import_tax_codes:
            journal_entry_payload.update({'GlobalTaxCalculation': 'TaxInclusive'})

            for line_item in journal_entry_lineitems:
                tax_code_id = line_item.tax_code if (line_item.tax_code and line_item.tax_amount is not None) else general_mappings.default_tax_code_id

                destination_attribute = DestinationAttribute.objects.filter(destination_id=tax_code_id, attribute_type='TAX_CODE', workspace_id=self.workspace_id).first()
                for tax_rate_ref in destination_attribute.detail['tax_refs']:
                    tax_rate_refs.append(tax_rate_ref)

            for tax_rate in tax_rate_refs:
                journal_entry_payload['TxnTaxDetail']['TaxLine'].append({"Amount": 0, "DetailType": "TaxLineDetail", 'TaxLineDetail': {'TaxRateRef': tax_rate, "PercentBased": True, "NetAmountTaxable": 0}})

        logger.info("| Payload for Journal Entry creation | Content: {{WORKSPACE_ID: {} EXPENSE_GROUP_ID: {} JOURNAL_ENTRY_PAYLOAD: {}}}".format(self.workspace_id, journal_entry.expense_group.id, journal_entry_payload))
        return journal_entry_payload

    def post_journal_entry(self, journal_entry: JournalEntry, journal_entry_lineitems: List[JournalEntryLineitem], single_credit_line: bool):
        """
        Post journal entries to QBO
        """
        try:
            journal_entry_payload = self.__construct_journal_entry(journal_entry, journal_entry_lineitems, single_credit_line)
            created_journal_entry = self.connection.journal_entries.post(journal_entry_payload)
            return created_journal_entry

        except WrongParamsError as bad_request:
            general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()
            response = json.loads(bad_request.response)
            if 'Fault' in response:
                error_response = json.loads(bad_request.response)['Fault']['Error'][0]

                if general_settings.change_accounting_period and 'account period closed' in error_response['Message'].lower():
                    book_closed_date = self.connection.preferences.get()['AccountingInfoPrefs']['BookCloseDate']
                    txn_date = datetime.strptime(book_closed_date, '%Y-%m-%d') + timedelta(days=1)
                    journal_entry_payload['TxnDate'] = txn_date.strftime("%Y-%m-%d")
                    created_journal_entry = self.connection.journal_entries.post(journal_entry_payload)

                    journal_entry.transaction_date = txn_date
                    journal_entry.save()
                    return created_journal_entry

            raise

    def get_company_preference(self):
        """
        Get QBO company preferences
        :return:
        """
        return self.connection.preferences.get()

    def get_company_info(self):
        """
        Get QBO company preferences
        :return:
        """
        return self.connection.company_info.get()

    def post_attachments(self, ref_id: str, ref_type: str, attachments: List[Dict]) -> List:
        """
        Link attachments to objects Quickbooks
        :param ref_id: object id
        :param ref_type: type of object
        :param attachments: attachment[dict()]
        :return: True for success, False for failure
        """

        if len(attachments):
            responses = []
            for attachment in attachments:
                # Ignoring html attachments from chrome extension, QBO API will throw error if we upload a html file
                if attachment['content_type'] != 'text/html':
                    response = self.connection.attachments.post(ref_id=ref_id, ref_type=ref_type, content=attachment['download_url'], file_name=attachment['name'].replace('jpeg', 'jpg'))
                    responses.append(response)
            return responses
        return []

    @staticmethod
    def __construct_bill_payment_lineitems(bill_payment_lineitems: List[BillPaymentLineitem]) -> List[Dict]:
        """
        Create bill payment line items
        :param bill_payment_lineitems: list of bill payment line items extracted from database
        :return: constructed line items
        """
        lines = []

        for line in bill_payment_lineitems:
            line = {'Amount': line.amount, 'LinkedTxn': [{"TxnId": line.linked_transaction_id, "TxnType": "Bill"}]}
            lines.append(line)

        return lines

    def __construct_bill_payment(self, bill_payment: BillPayment, bill_payment_lineitems: List[BillPaymentLineitem]) -> Dict:
        """
        Create a bill payment
        :param bill_payment: bill_payment object extracted from database
        :return: constructed bill payment
        """
        bill_payment_payload = {
            'VendorRef': {'value': bill_payment.vendor_id},
            'APAccountRef': {'value': bill_payment.accounts_payable_id},
            'DepartmentRef': {'value': bill_payment.department_id},
            'TxnDate': bill_payment.transaction_date,
            "CurrencyRef": {"value": bill_payment.currency},
            'PrivateNote': bill_payment.private_note,
            'TotalAmt': bill_payment.amount,
            'PayType': 'Check',
            'CheckPayment': {"BankAccountRef": {"value": bill_payment.payment_account}, "PrintStatus": "NotSet"},
            'Line': self.__construct_bill_payment_lineitems(bill_payment_lineitems),
        }

        logger.info("| Payload for Bill Payment creation | Content: {{WORKSPACE_ID: {} EXPENSE_GROUP_ID: {} BILL_PAYMENT_PAYLOAD: {}}}".format(self.workspace_id, bill_payment.expense_group.id, bill_payment_payload))
        return bill_payment_payload

    def post_bill_payment(self, bill_payment: BillPayment, bill_payment_lineitems: List[BillPaymentLineitem]):
        """
        Post bill payment to QBO
        """
        bill_payment_payload = self.__construct_bill_payment(bill_payment, bill_payment_lineitems)
        created_bill_payment = self.connection.bill_payments.post(bill_payment_payload)
        return created_bill_payment

    def create_credit_card_misc_vendor(self):
        created_vendor = self.get_or_create_vendor('Credit Card Misc', create=True)
        return created_vendor.destination_id

    def __get_entity_id(self, general_settings: WorkspaceGeneralSettings, value: str, employee_field_mapping: str,
    fund_source: str):
        if fund_source == 'PERSONAL' or (fund_source == 'CCC' and general_settings.name_in_journal_entry == 'EMPLOYEE'):
            entity = EmployeeMapping.objects.get(
                source_employee__value=value,
                workspace_id=general_settings.workspace_id
            )
            return entity.destination_employee.destination_id if employee_field_mapping == 'EMPLOYEE' else entity.destination_vendor.destination_id
        elif general_settings.name_in_journal_entry == 'MERCHANT' and general_settings.auto_create_merchants_as_vendors and value:
            created_vendor = self.get_or_create_vendor(value, create=True)
            if not created_vendor:
                return self.create_credit_card_misc_vendor()
            return created_vendor.destination_id
        else:
            return self.create_credit_card_misc_vendor()

    def get_or_create_entity(self, expense_group: ExpenseGroup, general_settings: WorkspaceGeneralSettings):
        entity_map = {}
        expenses = expense_group.expenses.all()
        employee_field_mapping = general_settings.employee_field_mapping
        for lineitem in expenses:
            if expense_group.fund_source == 'PERSONAL':
                entity_id = self.__get_entity_id(general_settings,
                    expense_group.description.get('employee_email'),
                    employee_field_mapping, expense_group.fund_source)
            elif general_settings.name_in_journal_entry == 'MERCHANT':
                vendor = DestinationAttribute.objects.filter(value__iexact=lineitem.vendor,
                workspace_id=expense_group.workspace_id, attribute_type='VENDOR').first()
                if vendor:
                    entity_id = vendor.destination_id
                else:
                    entity_id = self.__get_entity_id(general_settings, lineitem.vendor,
                        employee_field_mapping, expense_group.fund_source)
            else:
                entity_id = self.__get_entity_id(general_settings,
                    expense_group.description.get('employee_email'),
                    employee_field_mapping, expense_group.fund_source)

            entity_map[lineitem.id] = entity_id

        return entity_map
