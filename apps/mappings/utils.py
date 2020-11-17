import logging
import traceback
from typing import Dict, List

from django.db.models import Q

from apps.fyle.utils import FyleConnector
from apps.quickbooks_online.utils import QBOConnector
from fyle_accounting_mappings.models import MappingSetting, DestinationAttribute, Mapping

from apps.workspaces.models import WorkspaceGeneralSettings, FyleCredential, QBOCredential
from fyle_qbo_api.utils import assert_valid
from fylesdk import WrongParamsError

from .models import GeneralMapping

logger = logging.getLogger(__name__)


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
            'default_ccc_account_id': None,
            'default_ccc_vendor_name': None,
            'default_ccc_vendor_id': None
        }

        mapping_setting = MappingSetting.objects.filter(
            Q(destination_field='VENDOR') | Q(destination_field='EMPLOYEE'),
            source_field='EMPLOYEE', workspace_id=self.__workspace_id
        ).first()

        if mapping_setting.destination_field == 'VENDOR' or\
                general_settings.corporate_credit_card_expenses_object == 'BILL':
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

        general_mapping, _ = GeneralMapping.objects.update_or_create(
            workspace_id=self.__workspace_id,
            defaults=params
        )
        return general_mapping

    @staticmethod
    def create_fyle_projects_payload(projects: List[DestinationAttribute]):
        """
        Create Fyle Projects Payload from QBO Customer / Projects
        :param projects: QBO Projects
        :return: Fyle Projects Payload
        """
        payload = []

        for project in projects:
            payload.append({
                'name': project.value,
                'code': project.destination_id,
                'description': 'Quickbooks Online Customer / Project - {0}, Id - {1}'.format(
                    project.value,
                    project.destination_id
                ),
                'active': True if project.active is None else project.active
            })

        return payload

    def upload_projects_to_fyle(self):
        """
        Upload projects to Fyle
        """
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=self.__workspace_id)
        qbo_credentials: QBOCredential = QBOCredential.objects.get(workspace_id=self.__workspace_id)

        fyle_connection = FyleConnector(
            refresh_token=fyle_credentials.refresh_token,
            workspace_id=self.__workspace_id
        )

        qbo_connection = QBOConnector(
            credentials_object=qbo_credentials,
            workspace_id=self.__workspace_id
        )

        qbo_attributes: List[DestinationAttribute] = qbo_connection.sync_customers()

        fyle_payload: List[Dict] = self.create_fyle_projects_payload(qbo_attributes)

        fyle_projects = fyle_connection.connection.Projects.post(fyle_payload)
        fyle_connection.sync_projects(fyle_projects)
        return qbo_attributes

    def auto_create_project_mappings(self):
        """
        Create Project Mappings
        :return: mappings
        """
        MappingSetting.bulk_upsert_mapping_setting([{
            'source_field': 'PROJECT',
            'destination_field': 'CUSTOMER'
        }], workspace_id=self.__workspace_id)

        fyle_projects = self.upload_projects_to_fyle()

        project_mappings = []

        try:
            for project in fyle_projects:
                mapping = Mapping.create_or_update_mapping(
                    source_type='PROJECT',
                    destination_type='CUSTOMER',
                    source_value=project.value,
                    destination_value=project.value,
                    workspace_id=self.__workspace_id
                )
                project_mappings.append(mapping)

            return project_mappings
        except WrongParamsError as exception:
            logger.exception(
                'Error while creating projects workspace_id - %s in Fyle %s %s',
                self.__workspace_id, exception.message, {'error': exception.response}
            )
        except Exception:
            error = traceback.format_exc()
            error = {
                'error': error
            }
            logger.exception(
                'Error while creating projects workspace_id - %s error: %s',
                self.__workspace_id, error
            )
