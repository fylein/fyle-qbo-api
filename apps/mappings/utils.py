from typing import Dict

from django.db.models import Q

from apps.quickbooks_online.tasks import schedule_bill_payment_creation
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_qbo_api.utils import assert_valid

from .tasks import schedule_auto_map_ccc_employees

from .models import GeneralMapping


class MappingUtils:
    def __init__(self, workspace_id):
        self.__workspace_id = workspace_id

    def create_or_update_general_mapping(self, general_mapping: Dict):
        """
        Create or update general mapping
        :param general_mapping: general mapping payload
        :return:
        """
        general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=self.__workspace_id)

        params = {
            'accounts_payable_name': None,
            'accounts_payable_id': None,
            'qbo_expense_account_name': None,
            'qbo_expense_account_id': None,
            'bank_account_name': None,
            'bank_account_id': None,
            'default_ccc_account_name': None,
            'default_ccc_account_id': None,
            'default_ccc_vendor_name': None,
            'default_ccc_vendor_id': None
        }

        if (general_settings.employee_field_mapping == 'VENDOR' or
                general_settings.corporate_credit_card_expenses_object == 'BILL'):
            assert_valid('accounts_payable_name' in general_mapping and general_mapping['accounts_payable_name'],
                         'account payable account name field is blank')
            assert_valid('accounts_payable_id' in general_mapping and general_mapping['accounts_payable_id'],
                         'account payable account id field is blank')

            params['accounts_payable_name'] = general_mapping.get('accounts_payable_name')
            params['accounts_payable_id'] = general_mapping.get('accounts_payable_id')

        if general_settings.employee_field_mapping == 'EMPLOYEE' and \
                general_settings.reimbursable_expenses_object != 'EXPENSE':
            assert_valid('bank_account_name' in general_mapping and general_mapping['bank_account_name'],
                         'bank account name field is blank')
            assert_valid('bank_account_id' in general_mapping and general_mapping['bank_account_id'],
                         'bank account id field is blank')

            params['bank_account_name'] = general_mapping.get('bank_account_name')
            params['bank_account_id'] = general_mapping.get('bank_account_id')

        if general_settings.corporate_credit_card_expenses_object and \
                general_settings.corporate_credit_card_expenses_object != 'BILL':
            assert_valid('default_ccc_account_name' in general_mapping and general_mapping['default_ccc_account_name'],
                         'default ccc account name field is blank')
            assert_valid('default_ccc_account_id' in general_mapping and general_mapping['default_ccc_account_id'],
                         'default ccc account id field is blank')

            params['default_ccc_account_name'] = general_mapping.get('default_ccc_account_name')
            params['default_ccc_account_id'] = general_mapping.get('default_ccc_account_id')

        if general_settings.corporate_credit_card_expenses_object == 'BILL':
            assert_valid('default_ccc_vendor_name' in general_mapping and general_mapping['default_ccc_vendor_name'],
                         'default ccc vendor name field is blank')
            assert_valid('default_ccc_vendor_id' in general_mapping and general_mapping['default_ccc_vendor_id'],
                         'default ccc vendor id field is blank')

            params['default_ccc_vendor_name'] = general_mapping.get('default_ccc_vendor_name')
            params['default_ccc_vendor_id'] = general_mapping.get('default_ccc_vendor_id')

        if general_settings.sync_fyle_to_qbo_payments:
            assert_valid(
                'bill_payment_account_name' in general_mapping and general_mapping['bill_payment_account_name'],
                'bill payment account name field is blank')
            assert_valid(
                'bill_payment_account_id' in general_mapping and general_mapping['bill_payment_account_id'],
                'bill payment account id field is blank')

            params['bill_payment_account_name'] = general_mapping.get('bill_payment_account_name')
            params['bill_payment_account_id'] = general_mapping.get('bill_payment_account_id')

        if general_settings.reimbursable_expenses_object == 'EXPENSE':
            assert_valid('qbo_expense_account_name' in general_mapping and general_mapping['qbo_expense_account_name'],
                         'qbo expense account name field is blank')
            assert_valid('qbo_expense_account_id' in general_mapping and general_mapping['qbo_expense_account_id'],
                         'qbo expense account id field is blank')

            params['qbo_expense_account_name'] = general_mapping.get('qbo_expense_account_name')
            params['qbo_expense_account_id'] = general_mapping.get('qbo_expense_account_id')

        general_mapping_object, _ = GeneralMapping.objects.update_or_create(
            workspace_id=self.__workspace_id,
            defaults=params
        )

        schedule_bill_payment_creation(
            sync_fyle_to_qbo_payments=general_settings.sync_fyle_to_qbo_payments,
            workspace_id=self.__workspace_id
        )

        schedule_auto_map_ccc_employees(self.__workspace_id)
        return general_mapping_object
