from typing import List, Dict

from django.conf import settings

from qbosdk import QuickbooksOnlineSDK

from apps.workspaces.models import QBOCredential
from fyle_accounting_mappings.models import DestinationAttribute

from .models import BillLineitem, Bill, ChequeLineitem, Cheque, CreditCardPurchase, CreditCardPurchaseLineitem, \
    JournalEntry, JournalEntryLineitem


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
        else:
            attribute_type = 'ACCOUNTS_PAYABLE'
            display_name = 'Accounts Payable'

        for account in accounts:
            account_attributes.append({
                'attribute_type': attribute_type,
                'display_name': display_name,
                'value': account['Name'],
                'destination_id': account['Id'],
                'active': account['Active']
            })

        account_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            account_attributes, self.workspace_id)
        return account_attributes

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

        account_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            department_attributes, self.workspace_id)
        return account_attributes

    def sync_vendors(self):
        """
        Get vendors
        """
        vendors = self.connection.vendors.get()

        vendor_attributes = []

        for vendor in vendors:
            vendor_attributes.append({
                'attribute_type': 'VENDOR',
                'display_name': 'vendor',
                'value': vendor['DisplayName'],
                'destination_id': vendor['Id']
            })

        account_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            vendor_attributes, self.workspace_id)
        return account_attributes

    def sync_employees(self):
        """
        Get employees
        """
        employees = self.connection.employees.get()

        employee_attributes = []

        for employee in employees:
            employee_attributes.append({
                'attribute_type': 'EMPLOYEE',
                'display_name': 'employee',
                'value': employee['DisplayName'],
                'destination_id': employee['Id']
            })

        account_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            employee_attributes, self.workspace_id)
        return account_attributes

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

        account_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            class_attributes, self.workspace_id)
        return account_attributes

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
                'value': customer['FullyQualifiedName'],
                'destination_id': customer['Id'],
                'active': customer['Active']
            })

        account_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            customer_attributes, self.workspace_id)
        return account_attributes

    @staticmethod
    def purchase_object_payload(purchase_object, line, payment_type, account_ref, doc_number):
        """
        returns purchase object payload
        """
        purchase_object_payload = {
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
            cheque, line, account_ref=cheque.bank_account_id, payment_type='Check', doc_number=cheque.cheque_number
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
