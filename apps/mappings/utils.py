from typing import Dict

from fyle_qbo_api.utils import assert_valid

from .models import GeneralMapping, EmployeeMapping, CategoryMapping, CostCenterMapping, ProjectMapping


class MappingUtils:
    def __init__(self, workspace_id):
        self.__workspace_id = workspace_id

    def create_or_update_general_mapping(self, general_mapping: Dict):
        """
        Create or update general mapping
        :param general_mapping: general mapping payload
        :return:
        """
        # assert_valid('default_ccc_account_name' in general_mapping and general_mapping['default_ccc_account_name'],
        #              'default ccc account name field is blank')
        # assert_valid('default_ccc_account_id' in general_mapping and general_mapping['default_ccc_account_id'],
        #              'default ccc account id field is blank')

        general_mapping, _ = GeneralMapping.objects.update_or_create(
            workspace_id=self.__workspace_id,
            defaults={
                'account_payable_bank_account_name': general_mapping.get('account_payable_bank_account_name')
                if general_mapping.get(
                    'account_payable_bank_account_name') else general_mapping.get('account_payable_bank_account_name',
                                                                                  ''),

                'account_payable_bank_account_id': general_mapping.get('account_payable_bank_account_id')
                if general_mapping.get(
                    'account_payable_bank_account_id') else general_mapping.get('account_payable_bank_account_id', ''),

                'bank_account_name': general_mapping.get('bank_account_name') if general_mapping.get(
                    'bank_account_name') else general_mapping.get('bank_account_name', ''),

                'bank_account_id': general_mapping.get('bank_account_id') if general_mapping.get(
                    'bank_account_id') else general_mapping.get('bank_account_id', ''),

                'ccc_account_name': general_mapping.get('ccc_account_name') if general_mapping.get(
                    'ccc_account_name') else general_mapping.get('ccc_account_name', ''),

                'ccc_account_id': general_mapping.get('ccc_account_id') if general_mapping.get(
                    'ccc_account_id') else general_mapping.get('ccc_account_id', '')
            }
        )
        return general_mapping

    def create_or_update_employee_mapping(self, employee_mapping: Dict):
        """
        Create or update employee mappings
        :param employee_mapping: employee mapping payload
        :return: employee mappings objects
        """
        assert_valid('employee_email' in employee_mapping and employee_mapping['employee_email'],
                     'employee email field is blank')

        employee_mapping_object, _ = EmployeeMapping.objects.update_or_create(
            employee_email=employee_mapping['employee_email'].lower(),
            workspace_id=self.__workspace_id,
            defaults={
                'vendor_display_name': employee_mapping['vendor_display_name'] if employee_mapping.get(
                    'vendor_display_name') else employee_mapping.get('vendor_name', ''),
                'vendor_id': employee_mapping['vendor_id'] if employee_mapping.get(
                    'vendor_id') else employee_mapping.get('vendor_id', ''),
                'employee_display_name': employee_mapping['employee_display_name'] if employee_mapping.get(
                    'employee_display_name') else employee_mapping.get('employee_display_name', ''),
                'employee_id': employee_mapping['employee_id'] if employee_mapping.get(
                    'employee_id') else employee_mapping.get('employee_id', ''),
                'ccc_account_name': employee_mapping['ccc_account_name'] if employee_mapping.get(
                    'ccc_account_name') else employee_mapping.get('ccc_account_name', ''),
                'ccc_account_id': employee_mapping['ccc_account_id'] if employee_mapping.get(
                    'ccc_account_id') else employee_mapping.get('ccc_account_id', '')
            }
        )

        return employee_mapping_object

    def create_or_update_category_mapping(self, category_mapping: Dict):
        """
        Create or update category mappings
        :param category_mapping: category mapping payload
        :return: category mappings objects
        """
        assert_valid('category' in category_mapping and category_mapping['category'],
                     'category field is blank')
        assert_valid('sub_category' in category_mapping and category_mapping['sub_category'],
                     'sub_category field is blank')
        assert_valid('account_name' in category_mapping and category_mapping['account_name'],
                     'account name field is blank')
        assert_valid('account_id' in category_mapping and category_mapping['account_id'],
                     'account id field is blank')

        category_mapping_object, _ = CategoryMapping.objects.update_or_create(
            category=category_mapping['category'],
            sub_category=category_mapping['sub_category'],
            workspace_id=self.__workspace_id,
            defaults={
                'account_name': category_mapping['account_name'],
                'account_id': category_mapping['account_id']
            }
        )

        return category_mapping_object

    def create_or_update_cost_center_mapping(self, cost_center_mapping: Dict):
        """
        Create or update cost_center mappings
        :param cost_center_mapping: cost_center mapping payload
        :return: cost_center mappings objects
        """
        assert_valid('cost_center' in cost_center_mapping and cost_center_mapping['cost_center'],
                     'cost_center field is blank')
        assert_valid('class_name' in cost_center_mapping and cost_center_mapping['class_name'],
                     'class name field is blank')
        assert_valid('class_id' in cost_center_mapping and cost_center_mapping['class_id'],
                     'class id field is blank')

        cost_center_mapping_object, _ = CostCenterMapping.objects.update_or_create(
            cost_center=cost_center_mapping['cost_center'],
            workspace_id=self.__workspace_id,
            defaults={
                'class_name': cost_center_mapping['class_name'],
                'class_id': cost_center_mapping['class_id']
            }
        )

        return cost_center_mapping_object

    def create_or_update_project_mapping(self, project_mapping: Dict):
        """
        Create or update project mappings
        :param project_mapping: project mapping payload
        :return: project mappings objects
        """
        assert_valid('project' in project_mapping and project_mapping['project'],
                     'project field is blank')
        assert_valid('customer_display_name' in project_mapping and project_mapping['customer_display_name'],
                     'customer name field is blank')
        assert_valid('customer_id' in project_mapping and project_mapping['customer_id'],
                     'customer id field is blank')

        project_mapping_object, _ = ProjectMapping.objects.update_or_create(
            project=project_mapping['project'],
            workspace_id=self.__workspace_id,
            defaults={
                'customer_display_name': project_mapping['customer_display_name'],
                'customer_id': project_mapping['customer_id']
            }
        )

        return project_mapping_object
