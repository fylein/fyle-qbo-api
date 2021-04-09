from typing import List, Dict

from django.conf import settings

from qbosdk import QuickbooksOnlineSDK

import unidecode

from fyle_accounting_mappings.models import ExpenseAttribute, DestinationAttribute

from apps.workspaces.models import QBOCredential, WorkspaceGeneralSettings

from .models import BillLineitem, Bill, ChequeLineitem, Cheque, CreditCardPurchase, CreditCardPurchaseLineitem, \
    JournalEntry, JournalEntryLineitem, BillPaymentLineitem, BillPayment


# To do: Add this function to Fyle accounting mappings library
def bulk_create_or_update_destination_attributes(
        attributes: List[Dict], attribute_type: str, workspace_id: int, update: bool = False):
    """
    Create Expense Attributes in bulk
    :param update: Update Pre-existing records or not
    :param attribute_type: Attribute type
    :param attributes: attributes = [{
        'attribute_type': Type of attribute,
        'display_name': Display_name of attribute_field,
        'value': Value of attribute,
        'destination_id': Fyle Id of the attribute,
        'detail': Extra Details of the attribute
    }]
    :param workspace_id: Workspace Id
    :return: created / updated attributes
    """
    attribute_destination_id_list = [attribute['destination_id'] for attribute in attributes]

    existing_attributes = DestinationAttribute.objects.filter(
        destination_id__in=attribute_destination_id_list, attribute_type=attribute_type,
        workspace_id=workspace_id).all()

    existing_attribute_destination_ids = []

    primary_key_map = {}

    for existing_attribute in existing_attributes:
        existing_attribute_destination_ids.append(existing_attribute.destination_id)
        primary_key_map[existing_attribute.destination_id] = existing_attribute.id

    attributes_to_be_created = []
    attributes_to_be_updated = []

    destination_ids_appended = []
    for attribute in attributes:
        if attribute['destination_id'] not in existing_attribute_destination_ids \
                and attribute['destination_id'] not in destination_ids_appended:
            destination_ids_appended.append(attribute['destination_id'])
            attributes_to_be_created.append(
                DestinationAttribute(
                    attribute_type=attribute_type,
                    display_name=attribute['display_name'],
                    value=attribute['value'],
                    destination_id=attribute['destination_id'],
                    detail=attribute['detail'] if 'detail' in attribute else None,
                    workspace_id=workspace_id
                )
            )
        else:
            if update:
                attributes_to_be_updated.append(
                    DestinationAttribute(
                        id=primary_key_map[attribute['destination_id']],
                        value=attribute['value'],
                        detail=attribute['detail'] if 'detail' in attribute else None,
                    )
                )
    if attributes_to_be_created:
        DestinationAttribute.objects.bulk_create(attributes_to_be_created, batch_size=50)

    if attributes_to_be_updated:
        DestinationAttribute.objects.bulk_update(attributes_to_be_updated, fields=['detail', 'value'], batch_size=50)


class QBOConnector:
    """
    QBO utility functions
    """

    def __init__(self, credentials_object: QBOCredential, workspace_id: int):
        client_id = settings.QBO_CLIENT_ID
        client_secret = settings.QBO_CLIENT_SECRET
        environment = settings.QBO_ENVIRONMENT

        self.connection = QuickbooksOnlineSDK(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=credentials_object.refresh_token,
            realm_id=credentials_object.realm_id,
            environment=environment
        )

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
        vendor_name = vendor_name.replace("'", "\\'")  # Replacing ' with \\'
        vendor_name = vendor_name.replace('#', '%23')  # Replace '#' with %23

        vendor = self.connection.vendors.search_vendor_by_display_name(vendor_name)

        if not vendor:
            if create:
                created_vendor = self.post_vendor(vendor_name, email)
                return self.create_vendor_destionation_attribute(created_vendor)
            else:
                return
        else:
            return self.create_vendor_destionation_attribute(vendor)

    def sync_accounts(self, account_type: str):
        """
        Get accounts
        """
        accounts = self.connection.accounts.get()

        accounts = list(filter(lambda current_account: current_account['AccountType'] == account_type, accounts))

        account_attributes = []

        if account_type == 'Expense':
            attribute_type = 'ACCOUNT'
            display_name = 'Account'
        elif account_type == 'Credit Card':
            attribute_type = 'CREDIT_CARD_ACCOUNT'
            display_name = 'Credit Card Account'
        elif account_type == 'Bank':
            attribute_type = 'BANK_ACCOUNT'
            display_name = 'Bank Account'
        elif account_type == 'Bank' or account_type == 'Credit Card':
            attribute_type = 'BILL_PAYMENT_ACCOUNT'
            display_name = 'Bill Payment Account'
        else:
            attribute_type = 'ACCOUNTS_PAYABLE'
            display_name = 'Accounts Payable'

        category_sync_version = 'v2'
        general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()
        if general_settings:
            category_sync_version = general_settings.category_sync_version

        for account in accounts:
            attribute = {
                'attribute_type': attribute_type,
                'display_name': display_name,
                'value': unidecode.unidecode(u'{0}'.format(
                    account['Name'] if category_sync_version == 'v1' else account['FullyQualifiedName'])),
                'destination_id': account['Id'],
                'active': account['Active'],
                'detail': {
                    'fully_qualified_name': account['FullyQualifiedName']
                }
            }

            if account_type == 'Expense':
                attribute['value'] = attribute['value'].replace('/', '-')

            account_attributes.append(attribute)

        bulk_create_or_update_destination_attributes(account_attributes, attribute_type, self.workspace_id, True)
        return []

    def sync_departments(self):
        """
        Get departments
        """
        departments = self.connection.departments.get()

        department_attributes = []

        for department in departments:
            department_attributes.append({
                'attribute_type': 'DEPARTMENT',
                'display_name': 'Department',
                'value': department['Name'],
                'destination_id': department['Id']
            })

        bulk_create_or_update_destination_attributes(department_attributes, 'DEPARTMENT', self.workspace_id, True)
        return []

    def sync_vendors(self):
        """
        Get vendors
        """
        vendors = self.connection.vendors.get()

        vendor_attributes = []

        for vendor in vendors:
            detail = {
                'email': vendor['PrimaryEmailAddr']['Address']
                if (
                        'PrimaryEmailAddr' in vendor and
                        vendor['PrimaryEmailAddr'] and
                        'Address' in vendor['PrimaryEmailAddr'] and
                        vendor['PrimaryEmailAddr']['Address']
                ) else None
            }

            vendor_attributes.append({
                'attribute_type': 'VENDOR',
                'display_name': 'vendor',
                'value': vendor['DisplayName'],
                'destination_id': vendor['Id'],
                'detail': detail
            })

        bulk_create_or_update_destination_attributes(vendor_attributes, 'VENDOR', self.workspace_id, True)
        return []

    def create_vendor_destionation_attribute(self, vendor):
        created_vendor = DestinationAttribute.bulk_upsert_destination_attributes([{
            'attribute_type': 'VENDOR',
            'display_name': 'vendor',
            'value': vendor['DisplayName'],
            'destination_id': vendor['Id'],
            'detail': {
                'email': vendor['PrimaryEmailAddr']['Address'] if 'PrimaryEmailAddr' in vendor else None
            }
        }], self.workspace_id)[0]

        return created_vendor

    def post_vendor(self, vendor_name: str, email: str):
        """
        Create an Vendor on Quickbooks online
        :param email: email for employee vendors
        :param vendor_name: vendor attribute to be created
        :return: Vendor Desination Atribute
        """

        vendor = {
            'GivenName': vendor_name.split(' ')[0] if email else None,
            'FamilyName': (
                vendor_name.split(' ')[-1]if len(vendor_name.split(' ')) > 1 else ''
            ) if email else None,
            'DisplayName': vendor_name,
            'PrimaryEmailAddr': {
                'Address': email
            }
        }
        created_vendor = self.connection.vendors.post(vendor)['Vendor']

        return created_vendor

    def sync_employees(self):
        """
        Get employees
        """
        employees = self.connection.employees.get()

        employee_attributes = []

        for employee in employees:
            detail = {
                'email': employee['PrimaryEmailAddr']['Address']
                if (
                        'PrimaryEmailAddr' in employee and
                        employee['PrimaryEmailAddr'] and
                        'Address' in employee['PrimaryEmailAddr'] and
                        employee['PrimaryEmailAddr']['Address']
                ) else None
            }

            employee_attributes.append({
                'attribute_type': 'EMPLOYEE',
                'display_name': 'employee',
                'value': employee['DisplayName'],
                'destination_id': employee['Id'],
                'detail': detail
            })

        bulk_create_or_update_destination_attributes(employee_attributes, 'EMPLOYEE', self.workspace_id, True)
        return []

    def post_employee(self, employee: ExpenseAttribute, auto_map_employee_preference: str):
        """
        Create an Employee on Quickbooks online
        :param auto_map_employee_preference: Auto map employee preference chosen
        :param employee: employee attribute to be created
        :return: Employee Desination Atribute
        """
        quickbooks_display_name = employee.detail['full_name']

        employee = {
            'GivenName': quickbooks_display_name.split(' ')[0],
            'FamilyName': quickbooks_display_name.split(' ')[-1]
            if len(quickbooks_display_name.split(' ')) > 1 else '',
            'DisplayName': quickbooks_display_name,
            'PrimaryEmailAddr': {
                'Address': employee.value
            }
        }

        created_employee = self.connection.employees.post(employee)['Employee']

        created_employee = DestinationAttribute.bulk_upsert_destination_attributes([{
            'attribute_type': 'EMPLOYEE',
            'display_name': 'employee',
            'value': created_employee['DisplayName'],
            'destination_id': created_employee['Id'],
            'detail': {
                'email': created_employee['PrimaryEmailAddr']['Address']
            }
        }], self.workspace_id)[0]

        return created_employee

    def sync_classes(self):
        """
        Get classes
        """
        classes = self.connection.classes.get()

        class_attributes = []

        for qbo_class in classes:
            class_attributes.append({
                'attribute_type': 'CLASS',
                'display_name': 'class',
                'value': qbo_class['Name'],
                'destination_id': qbo_class['Id']
            })

        bulk_create_or_update_destination_attributes(class_attributes, 'CLASS', self.workspace_id, True)
        return []

    def sync_customers(self):
        """
        Get customers
        """
        customers = self.connection.customers.get()

        customer_attributes = []

        for customer in customers:
            customer_attributes.append({
                'attribute_type': 'CUSTOMER',
                'display_name': 'customer',
                'value': unidecode.unidecode(u'{0}'.format(customer['FullyQualifiedName'])),
                'destination_id': customer['Id'],
                'active': customer['Active']
            })

        bulk_create_or_update_destination_attributes(customer_attributes, 'CUSTOMER', self.workspace_id, True)
        return []

    @staticmethod
    def purchase_object_payload(purchase_object, line, payment_type, account_ref, doc_number: str = None):
        """
        returns purchase object payload
        """
        purchase_object_payload = {
            'DocNumber': doc_number if doc_number else None,
            'PaymentType': payment_type,
            'AccountRef': {
                'value': account_ref
            },
            'EntityRef': {
                'value': purchase_object.entity_id
            },
            'DepartmentRef': {
                'value': purchase_object.department_id
            },
            'TxnDate': purchase_object.transaction_date,
            "CurrencyRef": {
                "value": purchase_object.currency
            },
            'PrivateNote': purchase_object.private_note,
            'Line': line
        }
        return purchase_object_payload

    @staticmethod
    def __construct_bill_lineitems(bill_lineitems: List[BillLineitem]) -> List[Dict]:
        """
        Create bill line items
        :param bill_lineitems: list of bill line items extracted from database
        :return: constructed line items
        """
        lines = []

        for line in bill_lineitems:
            line = {
                'Description': line.description,
                'DetailType': 'AccountBasedExpenseLineDetail',
                'Amount': line.amount,
                'AccountBasedExpenseLineDetail': {
                    'AccountRef': {
                        'value': line.account_id
                    },
                    'CustomerRef': {
                        'value': line.customer_id
                    },
                    'ClassRef': {
                        'value': line.class_id
                    },
                    'BillableStatus': 'Billable' if line.billable and line.customer_id else 'NotBillable'
                }
            }
            lines.append(line)

        return lines

    def __construct_bill(self, bill: Bill, bill_lineitems: List[BillLineitem]) -> Dict:
        """
        Create a bill
        :param bill: bill object extracted from database
        :return: constructed bill
        """
        bill_payload = {
            'VendorRef': {
                'value': bill.vendor_id
            },
            'APAccountRef': {
                'value': bill.accounts_payable_id
            },
            'DepartmentRef': {
                'value': bill.department_id
            },
            'TxnDate': bill.transaction_date,
            "CurrencyRef": {
                "value": bill.currency
            },
            'PrivateNote': bill.private_note,
            'Line': self.__construct_bill_lineitems(bill_lineitems)
        }

        return bill_payload

    def post_bill(self, bill: Bill, bill_lineitems: List[BillLineitem]):
        """
        Post bills to QBO
        """
        bills_payload = self.__construct_bill(bill, bill_lineitems)
        created_bill = self.connection.bills.post(bills_payload)
        return created_bill

    def get_bill(self, bill_id):
        """
        GET bill from QBO
        """
        bill = self.connection.bills.get_by_id(bill_id)
        return bill

    @staticmethod
    def __construct_cheque_lineitems(cheque_lineitems: List[ChequeLineitem]) -> List[Dict]:
        """
        Create cheque lineitems
        :param cheque_lineitems: list of cheque line items extracted from database
        :return: constructed line items
        """
        lines = []
        for line in cheque_lineitems:
            line = {
                'Description': line.description,
                'DetailType': 'AccountBasedExpenseLineDetail',
                'Amount': line.amount,
                'AccountBasedExpenseLineDetail': {
                    'AccountRef': {
                        'value': line.account_id
                    },
                    'ClassRef': {
                        'value': line.class_id
                    },
                    'CustomerRef': {
                        'value': line.customer_id
                    },
                    'BillableStatus': 'Billable' if line.billable and line.customer_id else 'NotBillable'
                }
            }
            lines.append(line)

        return lines

    def __construct_cheque(self, cheque: Cheque, cheque_lineitems: List[ChequeLineitem]) -> Dict:
        """
        Create a cheque
        :param cheque: cheque object extracted from database
        :return: constructed cheque
        """
        line = self.__construct_cheque_lineitems(cheque_lineitems)
        cheque_payload = self.purchase_object_payload(
            cheque, line, account_ref=cheque.bank_account_id, payment_type='Check'
        )
        return cheque_payload

    def post_cheque(self, cheque: Cheque, cheque_lineitems: List[ChequeLineitem]):
        """
        Post cheque to QBO
        """
        cheques_payload = self.__construct_cheque(cheque, cheque_lineitems)
        created_cheque = self.connection.purchases.post(cheques_payload)
        return created_cheque

    @staticmethod
    def __construct_credit_card_purchase_lineitems(
            credit_card_purchase_lineitems: List[CreditCardPurchaseLineitem]) -> List[Dict]:
        """
        Create credit_card_purchase line items
        :param credit_card_purchase_lineitems: list of credit_card_purchase line items extracted from database
        :return: constructed line items
        """
        lines = []

        for line in credit_card_purchase_lineitems:
            line = {
                'Description': line.description,
                'DetailType': 'AccountBasedExpenseLineDetail',
                'Amount': line.amount,

                'AccountBasedExpenseLineDetail': {
                    'AccountRef': {
                        'value': line.account_id
                    },
                    'CustomerRef': {
                        'value': line.customer_id
                    },
                    'ClassRef': {
                        'value': line.class_id
                    },
                    'BillableStatus': 'Billable' if line.billable and line.customer_id else 'NotBillable'
                },
            }
            lines.append(line)

        return lines

    def __construct_credit_card_purchase(self, credit_card_purchase: CreditCardPurchase,
                                         credit_card_purchase_lineitems: List[CreditCardPurchaseLineitem]) -> Dict:
        """
        Create a credit_card_purchase
        :param credit_card_purchase: credit_card_purchase object extracted from database
        :return: constructed credit_card_purchase
        """
        line = self.__construct_credit_card_purchase_lineitems(credit_card_purchase_lineitems)
        credit_card_purchase_payload = self.purchase_object_payload(
            credit_card_purchase, line, account_ref=credit_card_purchase.ccc_account_id, payment_type='CreditCard',
            doc_number=credit_card_purchase.credit_card_purchase_number
        )

        return credit_card_purchase_payload

    def post_credit_card_purchase(self, credit_card_purchase: CreditCardPurchase,
                                  credit_card_purchase_lineitems: List[CreditCardPurchaseLineitem]):
        """
        Post bills to QBO
        """
        credit_card_purchase_payload = self.__construct_credit_card_purchase(credit_card_purchase,
                                                                             credit_card_purchase_lineitems)
        created_credit_card_purchase = self.connection.purchases.post(credit_card_purchase_payload)
        return created_credit_card_purchase

    @staticmethod
    def __construct_journal_entry_lineitems(journal_entry_lineitems: List[JournalEntryLineitem],
                                            posting_type) -> List[Dict]:
        """
        Create journal_entry line items
        :param journal_entry_lineitems: list of journal entry line items extracted from database
        :return: constructed line items
        """
        lines = []

        for line in journal_entry_lineitems:

            account_ref = None
            if posting_type == 'Debit':
                account_ref = line.account_id
            elif posting_type == 'Credit':
                account_ref = line.debit_account_id

            line = {
                'DetailType': 'JournalEntryLineDetail',
                'Description': line.description,
                'Amount': line.amount,
                'JournalEntryLineDetail': {
                    'PostingType': posting_type,
                    'AccountRef': {
                        'value': account_ref
                    },
                    'DepartmentRef': {
                        'value': line.department_id
                    },
                    'ClassRef': {
                        'value': line.class_id
                    },
                    'Entity': {
                        'EntityRef': {
                            'value': line.entity_id
                        },
                        'Type': line.entity_type,
                    }
                }
            }
            lines.append(line)

        return lines

    def __construct_journal_entry(self, journal_entry: JournalEntry,
                                  journal_entry_lineitems: List[JournalEntryLineitem]) -> Dict:
        """
        Create a journal_entry
        :param journal_entry: journal_entry object extracted from database
        :return: constructed journal_entry
        """
        credit_line = self.__construct_journal_entry_lineitems(journal_entry_lineitems, 'Credit')
        debit_line = self.__construct_journal_entry_lineitems(journal_entry_lineitems, 'Debit')
        lines = []
        lines.extend(credit_line)
        lines.extend(debit_line)

        journal_entry_payload = {
            'TxnDate': journal_entry.transaction_date,
            'PrivateNote': journal_entry.private_note,
            'Line': lines,
            'CurrencyRef': {
                "value": journal_entry.currency
            }
        }
        return journal_entry_payload

    def post_journal_entry(self, journal_entry: JournalEntry, journal_entry_lineitems: List[JournalEntryLineitem]):
        """
        Post journal entries to QBO
        """
        journal_entry_payload = self.__construct_journal_entry(journal_entry, journal_entry_lineitems)
        created_journal_entry = self.connection.journal_entries.post(journal_entry_payload)
        return created_journal_entry

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
        :param prep_id: prep id for export
        :param ref_id: object id
        :param ref_type: type of object
        :param attachments: attachment[dict()]
        :return: True for success, False for failure
        """

        if len(attachments):
            responses = []
            for attachment in attachments:
                response = self.connection.attachments.post(
                    ref_id=ref_id,
                    ref_type=ref_type,
                    content=attachment['content'],
                    file_name=attachment['filename']
                )
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
            line = {
                'Amount': line.amount,
                'LinkedTxn': [
                    {
                        "TxnId": line.linked_transaction_id,
                        "TxnType": "Bill"
                    }
                ]
            }
            lines.append(line)

        return lines

    def __construct_bill_payment(self, bill_payment: BillPayment,
                                 bill_payment_lineitems: List[BillPaymentLineitem]) -> Dict:
        """
        Create a bill payment
        :param bill_payment: bill_payment object extracted from database
        :return: constructed bill payment
        """
        bill_payment_payload = {
            'VendorRef': {
                'value': bill_payment.vendor_id
            },
            'APAccountRef': {
                'value': bill_payment.accounts_payable_id
            },
            'DepartmentRef': {
                'value': bill_payment.department_id
            },
            'TxnDate': bill_payment.transaction_date,
            "CurrencyRef": {
                "value": bill_payment.currency
            },
            'PrivateNote': bill_payment.private_note,
            'TotalAmt': bill_payment.amount,
            'PayType': 'Check',
            'CheckPayment': {
                "BankAccountRef": {
                    "value": bill_payment.payment_account
                }
            },
            'Line': self.__construct_bill_payment_lineitems(bill_payment_lineitems)
        }

        return bill_payment_payload

    def post_bill_payment(self, bill_payment: BillPayment, bill_payment_lineitems: List[BillPaymentLineitem]):
        """
        Post bill payment to QBO
        """
        bill_payment_payload = self.__construct_bill_payment(bill_payment, bill_payment_lineitems)
        created_bill_payment = self.connection.bill_payments.post(bill_payment_payload)
        return created_bill_payment
