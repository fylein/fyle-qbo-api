from typing import List, Dict

from django.conf import settings

from qbosdk import QuickbooksOnlineSDK

from apps.workspaces.models import QBOCredential

from .models import BillLineitem, Bill, ChequeLineitem, Cheque, CreditCardPurchase, CreditCardPurchaseLineitem,\
    JournalEntry, JournalEntryLineitem


class QBOConnector:
    """
    QBO utility functions
    """
    def __init__(self, credentials_object: QBOCredential):
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

        credentials_object.refresh_token = self.connection.refresh_token
        credentials_object.save()

    def get_accounts(self):
        """
        Get accounts
        """
        return self.connection.accounts.get()

    def get_departments(self):
        """
        Get departments
        """
        return self.connection.departments.get()

    def get_vendors(self):
        """
        Get vendors
        """
        return self.connection.vendors.get()

    def get_employees(self):
        """
        Get employees
        """
        return self.connection.employees.get()

    def get_classes(self):
        """
        Get classes
        """
        return self.connection.classes.get()

    def get_customers(self):
        """
        Get classes
        """
        return self.connection.customers.get()

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
            'Line': line,
            'DocNumber': doc_number
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
                    }
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
            'Line': self.__construct_bill_lineitems(bill_lineitems),
            'DocNumber': bill.bill_number
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
    def __construct_cheque_line_items(cheque_line_items: List[ChequeLineitem]) -> List[Dict]:
        """
        Create cheque line items
        :param cheque_line_items: list of cheque line items extracted from database
        :return: constructed line items
        """
        lines = []
        for line in cheque_line_items:
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
                    }
                }
            }
            lines.append(line)

        return lines

    def __construct_cheque(self, cheque: Cheque, cheque_line_items: List[ChequeLineitem]) -> Dict:
        """
        Create a cheque
        :param cheque: cheque object extracted from database
        :return: constructed cheque
        """
        line = self.__construct_cheque_line_items(cheque_line_items)
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
                    }
                }
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
    def __construct_journal_entry_line_items(journal_entry_line_items: List[JournalEntryLineitem],
                                             posting_type) -> List[Dict]:
        """
        Create journal_entry line items
        :param journal_entry_line_items: list of journal entry line items extracted from database
        :return: constructed line items
        """
        lines = []

        for line in journal_entry_line_items:
            line = {
                'DetailType': 'JournalEntryLineDetail',
                'Description': line.description,
                'Amount': line.amount,
                'JournalEntryLineDetail': {
                    'PostingType': posting_type,
                    'AccountRef': {
                        'value': line.account_id
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
                        }
                    }
                }
            }
            lines.append(line)

        return lines

    def __construct_journal_entry(self, journal_entry: JournalEntry,
                                  journal_entry_line_items: List[JournalEntryLineitem]) -> Dict:
        """
        Create a journal_entry
        :param journal_entry: journal_entry object extracted from database
        :return: constructed journal_entry
        """
        credit_line = self.__construct_journal_entry_line_items(journal_entry_line_items, 'Credit')
        debit_line = self.__construct_journal_entry_line_items(journal_entry_line_items, 'Debit')
        lines = credit_line + debit_line

        journal_entry_payload = {
            'TxnDate': journal_entry.transaction_date,
            'PrivateNote': journal_entry.private_note,
            'Line': lines,
            'CurrencyRef': {
                "value": journal_entry.currency
            },
            'DocNumber': journal_entry.journal_entry_number
        }
        return journal_entry_payload

    def post_journal_entry(self, journal_entry: JournalEntry, journal_entry_lineitems: List[JournalEntryLineitem]):
        """
        Post journal entries to QBO
        """
        journal_entry_payload = self.__construct_journal_entry(journal_entry, journal_entry_lineitems)
        created_journal_entry = self.connection.journal_entries.post(journal_entry_payload)
        return created_journal_entry
