from typing import Dict, List
from django.db.models import Q

from fyle_accounting_mappings.models import MappingSetting

from apps.fyle.models import ExpenseGroupSettings
from apps.workspaces.models import WorkspaceGeneralSettings

from apps.mappings.tasks import schedule_cost_centers_creation, \
    schedule_fyle_attributes_creation, schedule_projects_creation, schedule_tax_groups_creation


class ImportSettingsTrigger:
    """
    All the post save actions of Import Settings API
    """
    def __init__(self, workspace_general_settings: Dict, mapping_settings: List[Dict], workspace_id):
        self.__workspace_general_settings = workspace_general_settings
        self.__mapping_settings = mapping_settings
        self.__workspace_id = workspace_id

    def __remove_old_department_source_field(
            self,
            current_mappings_settings: List[MappingSetting],
            new_mappings_settings: List[Dict]
        ):
        """
        Should remove Department Source field from Reimbursable settings in case of deletion and updation
        """
        old_department_setting = current_mappings_settings.filter(
            destination_field='DEPARTMENT'
        ).first()

        new_department_setting = list(filter(
            lambda setting: setting['destination_field'] == 'DEPARTMENT',
            new_mappings_settings
        ))

        if (old_department_setting and new_department_setting and \
            old_department_setting.source_field != new_department_setting[0]['source_field']) or \
                (old_department_setting and not new_department_setting):
            expense_group_settings = ExpenseGroupSettings.objects.get(
                workspace_id=self.__workspace_id
            )

            # Removing Department Source field from Reimbursable settings
            reimbursable_settings = expense_group_settings.reimbursable_expense_group_fields
            reimbursable_settings.remove(old_department_setting.source_field.lower())
            expense_group_settings.reimbursable_expense_group_fields = list(set(reimbursable_settings))

            # Removing Department Source field from Non reimbursable settings
            corporate_credit_card_settings = list(expense_group_settings.corporate_credit_card_expense_group_fields)
            corporate_credit_card_settings.remove(old_department_setting.source_field.lower())
            expense_group_settings.corporate_credit_card_expense_group_fields = list(
                set(corporate_credit_card_settings)
            )

            expense_group_settings.save()


    def __update_expense_group_settings_for_departments(self):
        """
        Should group expenses by department source field in case the export is journal entries
        """
        workspace_general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.filter(
            workspace_id=self.__workspace_id).first()

        expense_group_settings: ExpenseGroupSettings = ExpenseGroupSettings.objects.get(
            workspace_id=self.__workspace_id
        )
        department_setting = list(filter(
            lambda setting: setting['destination_field'] == 'DEPARTMENT', self.__mapping_settings))

        if department_setting:
            department_setting = department_setting[0]

            # Adding Department Source field to Reimbursable settings
            reimbursable_settings = expense_group_settings.reimbursable_expense_group_fields

            if workspace_general_settings.reimbursable_expenses_object not in ('JOURNAL_ENTRY', None):
                reimbursable_settings.append(department_setting['source_field'].lower())
                expense_group_settings.reimbursable_expense_group_fields = list(set(reimbursable_settings))

            # Adding Department Source field to Non reimbursable settings
            corporate_credit_card_settings = list(expense_group_settings.corporate_credit_card_expense_group_fields)

            if workspace_general_settings.corporate_credit_card_expenses_object not in ('JOURNAL_ENTRY', None):
                corporate_credit_card_settings.append(department_setting['source_field'].lower())
                expense_group_settings.corporate_credit_card_expense_group_fields = list(
                    set(corporate_credit_card_settings)
                )

            expense_group_settings.save()

    def post_save_workspace_general_settings(self):
        """
        Post save action for workspace general settings
        """
        schedule_tax_groups_creation(
            import_tax_codes=self.__workspace_general_settings.get('import_tax_codes'),
            workspace_id=self.__workspace_id
        )

    def pre_save_mapping_settings(self):
        """
        Post save action for mapping settings
        """
        mapping_settings = self.__mapping_settings

        projects_mapping_available = False
        cost_center_mapping_available = False

        for setting in mapping_settings:
            if setting['source_field'] == 'PROJECT':
                projects_mapping_available = True
            elif setting['source_field'] == 'COST_CENTER':
                cost_center_mapping_available = True

        if not projects_mapping_available:
            schedule_projects_creation(False, self.__workspace_id)
        
        if not cost_center_mapping_available:
            schedule_cost_centers_creation(False, self.__workspace_id)
        
        schedule_fyle_attributes_creation(self.__workspace_id)

        current_mapping_settings = MappingSetting.objects.filter(workspace_id=self.__workspace_id).all()

        self.__remove_old_department_source_field(
            current_mappings_settings=current_mapping_settings,
            new_mappings_settings=mapping_settings
        )

    def post_save_mapping_settings(self):
        """
        Post save actions for mapping settings
        """
        destination_fields = []
        for setting in self.__mapping_settings:
            destination_fields.append(setting['destination_field'])

        MappingSetting.objects.filter(
            ~Q(destination_field__in=destination_fields),
            destination_field__in=['CLASS', 'CUSTOMER', 'DEPARTMENT'],
            workspace_id=self.__workspace_id
        ).delete()

        self.__update_expense_group_settings_for_departments()
