from typing import Dict

from django.db.models import Q

from fyle_accounting_mappings.models import MappingSetting

from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_qbo_api.utils import assert_valid

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
            'bank_account_name': None,
            'bank_account_id': None,
            'default_ccc_account_name': None,
            'default_ccc_account_id': None
        }

        mapping_setting = MappingSetting.objects.filter(
            Q(destination_field='VENDOR') | Q(destination_field='EMPLOYEE'),
            source_field='EMPLOYEE', workspace_id=self.__workspace_id
        ).first()

        if mapping_setting.destination_field == 'VENDOR':
            assert_valid('accounts_payable_name' in general_mapping and general_mapping['accounts_payable_name'],
                         'account payable account name field is blank')
            assert_valid('accounts_payable_id' in general_mapping and general_mapping['accounts_payable_id'],
                         'account payable account id field is blank')

            params['accounts_payable_name'] = general_mapping.get('accounts_payable_name')
            params['accounts_payable_id'] = general_mapping.get('accounts_payable_id')

        if mapping_setting.destination_field == 'EMPLOYEE':
            assert_valid('bank_account_name' in general_mapping and general_mapping['bank_account_name'],
                         'bank account name field is blank')
            assert_valid('bank_account_id' in general_mapping and general_mapping['bank_account_id'],
                         'bank account id field is blank')

            params['bank_account_name'] = general_mapping.get('bank_account_name')
            params['bank_account_id'] = general_mapping.get('bank_account_id')

        if general_settings.corporate_credit_card_expenses_object:
            assert_valid('default_ccc_account_name' in general_mapping and general_mapping['default_ccc_account_name'],
                         'default ccc account name field is blank')
            assert_valid('default_ccc_account_id' in general_mapping and general_mapping['default_ccc_account_id'],
                         'default ccc account id field is blank')

            params['default_ccc_account_name'] = general_mapping.get('default_ccc_account_name')
            params['default_ccc_account_id'] = general_mapping.get('default_ccc_account_id')

        general_mapping, _ = GeneralMapping.objects.update_or_create(
            workspace_id=self.__workspace_id,
            defaults=params
        )
        return general_mapping
