from typing import List, Dict

from django.conf import settings

from qbosdk import QuickbooksOnlineSDK

from apps.workspaces.models import QBOCredential

from .models import BillLineitem, Bill, CheckLineitem, QuickbooksCheck


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
    def __construct_check_line_items(check_line_items: List[CheckLineitem]) -> List[Dict]:
        """
        Create check line items
        :param check_line_items: list of check line items extracted from database
        :return: constructed line items
        """
        lines = []

        for line in check_line_items:
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

    def __construct_check(self, check: QuickbooksCheck, check_line_items: List[CheckLineitem]) -> Dict:
        """
        Create a check
        :param check: check object extracted from database
        :return: constructed check
        """
        check_payload = {
            'PaymentType': 'Check',
            'AccountRef': {
                'value': check.bank_account_id
            },
            'EntityRef': {
                'value': check.employee_id
            },
            'DepartmentRef': {
                'value': check.department_id
            },
            'TxnDate': check.transaction_date,
            "CurrencyRef": {
                "value": check.currency
            },
            'PrivateNote': check.private_note,
            'Line': self.__construct_check_line_items(check_line_items),
            'DocNumber': check.check_number
        }

        return check_payload

    def post_check(self, check: QuickbooksCheck, check_lineitems: List[CheckLineitem]):
        """
        Post checks to QBO
        """
        checks_payload = self.__construct_check(check, check_lineitems)
        created_check = self.connection.purchases.post(checks_payload)
        return created_check
