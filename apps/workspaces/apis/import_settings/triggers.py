from datetime import datetime, timezone
from typing import Dict, List

from django.db.models import Q
from django_q.tasks import async_task
from fyle_accounting_mappings.models import ExpenseAttribute, MappingSetting

from apps.fyle.models import ExpenseGroupSettings
from apps.mappings.schedules import schedule_or_delete_fyle_import_tasks as new_schedule_or_delete_fyle_import_tasks
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_integrations_imports.models import ImportLog


class ImportSettingsTrigger:
    """
    All the post save actions of Import Settings API
    """

    def __init__(self, workspace_general_settings: Dict, mapping_settings: List[Dict], workspace_id):
        self.__workspace_general_settings = workspace_general_settings
        self.__mapping_settings = mapping_settings
        self.__workspace_id = workspace_id

    def remove_department_grouping(self, source_field: str):
        workspace_general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.__workspace_id).first()
        expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=self.__workspace_id)

        # Removing Department Source field from Reimbursable settings
        if workspace_general_settings.reimbursable_expenses_object:
            reimbursable_settings = expense_group_settings.reimbursable_expense_group_fields
            if source_field.lower() in reimbursable_settings:
                reimbursable_settings.remove(source_field.lower())
            expense_group_settings.reimbursable_expense_group_fields = list(set(reimbursable_settings))

        # Removing Department Source field from Non reimbursable settings
        if workspace_general_settings.corporate_credit_card_expenses_object:
            corporate_credit_card_settings = list(expense_group_settings.corporate_credit_card_expense_group_fields)
            if source_field.lower() in corporate_credit_card_settings:
                corporate_credit_card_settings.remove(source_field.lower())
            expense_group_settings.corporate_credit_card_expense_group_fields = list(set(corporate_credit_card_settings))

        expense_group_settings.save()

    def add_department_grouping(self, source_field: str):
        workspace_general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.__workspace_id).first()

        expense_group_settings: ExpenseGroupSettings = ExpenseGroupSettings.objects.get(workspace_id=self.__workspace_id)

        # Adding Department Source field to Reimbursable settings
        reimbursable_settings = expense_group_settings.reimbursable_expense_group_fields

        if workspace_general_settings.reimbursable_expenses_object != 'JOURNAL_ENTRY':
            reimbursable_settings.append(source_field.lower())
            expense_group_settings.reimbursable_expense_group_fields = list(set(reimbursable_settings))

        # Adding Department Source field to Non reimbursable settings
        corporate_credit_card_settings = list(expense_group_settings.corporate_credit_card_expense_group_fields)

        if workspace_general_settings.corporate_credit_card_expenses_object != 'JOURNAL_ENTRY':
            corporate_credit_card_settings.append(source_field.lower())
            expense_group_settings.corporate_credit_card_expense_group_fields = list(set(corporate_credit_card_settings))

        expense_group_settings.save()

    def __update_expense_group_settings_for_departments(self):
        """
        Should group expenses by department source field in case the export is journal entries
        """
        department_setting = list(filter(lambda setting: setting['destination_field'] == 'DEPARTMENT', self.__mapping_settings))

        if department_setting:
            department_setting = department_setting[0]

            self.add_department_grouping(department_setting['source_field'])

    def post_save_workspace_general_settings(self, workspace_general_settings_instance: WorkspaceGeneralSettings, old_workspace_general_settings: WorkspaceGeneralSettings):
        """
        Post save action for workspace general settings
        """
        if not workspace_general_settings_instance.import_items and old_workspace_general_settings.import_items:
            async_task('fyle_integrations_imports.tasks.disable_items', workspace_id=self.__workspace_id, is_import_enabled=False)
        new_schedule_or_delete_fyle_import_tasks(workspace_general_settings_instance)

    def __remove_old_department_source_field(self, current_mappings_settings: List[MappingSetting], new_mappings_settings: List[Dict]):
        """
        Should remove Department Source field from Reimbursable settings in case of deletion and updation
        """
        old_department_setting = current_mappings_settings.filter(destination_field='DEPARTMENT').first()

        new_department_setting = list(filter(lambda setting: setting['destination_field'] == 'DEPARTMENT', new_mappings_settings))

        if old_department_setting and new_department_setting and old_department_setting.source_field != new_department_setting[0]['source_field']:
            self.remove_department_grouping(old_department_setting.source_field.lower())

    def __unset_auto_mapped_flag(self, current_mapping_settings: List[MappingSetting], new_mappings_settings: List[Dict]):
        """
        Set the auto_mapped flag to false for the expense_attributes for the attributes
        whose mapping is changed.
        """
        changed_source_fields = []

        for new_setting in new_mappings_settings:
            destination_field = new_setting['destination_field']
            source_field = new_setting['source_field']
            current_setting = current_mapping_settings.filter(destination_field=destination_field).first()
            if current_setting and current_setting.source_field != source_field:
                changed_source_fields.append(source_field)

        ExpenseAttribute.objects.filter(workspace_id=self.__workspace_id, attribute_type__in=changed_source_fields).update(auto_mapped=False)

    def __reset_import_log_timestamp(
            self,
            current_mapping_settings: List[MappingSetting],
            new_mappings_settings: List[Dict],
            workspace_id: int,
    ):
        """
        Reset Import logs when mapping settings are deleted or the source_field is changed.
        """
        changed_source_fields = set()

        for new_setting in new_mappings_settings:
            destination_field = new_setting['destination_field']
            source_field = new_setting['source_field']
            current_setting = current_mapping_settings.filter(source_field=source_field).first()
            if current_setting and current_setting.destination_field != destination_field:
                changed_source_fields.add(current_setting.source_field)

        current_source_fields = set(mapping_setting.source_field for mapping_setting in current_mapping_settings)
        new_source_fields = set(mapping_setting['source_field'] for mapping_setting in new_mappings_settings)
        deleted_source_fields = current_source_fields.difference(new_source_fields | {'CORPORATE_CARD', 'CATEGORY'})

        reset_source_fields = changed_source_fields.union(deleted_source_fields)

        ImportLog.objects.filter(workspace_id=workspace_id, attribute_type__in=reset_source_fields).update(last_successful_run_at=None, updated_at=datetime.now(timezone.utc))

    def pre_save_mapping_settings(self, pre_save_general_settings: WorkspaceGeneralSettings):
        """
        Post save action for mapping settings
        """
        mapping_settings = self.__mapping_settings

        # Update department mapping to some other Fyle field
        current_mapping_settings = MappingSetting.objects.filter(workspace_id=self.__workspace_id).all()

        self.__remove_old_department_source_field(current_mappings_settings=current_mapping_settings, new_mappings_settings=mapping_settings)
        self.__unset_auto_mapped_flag(current_mapping_settings=current_mapping_settings, new_mappings_settings=mapping_settings)
        self.__reset_import_log_timestamp(
            current_mapping_settings=current_mapping_settings,
            new_mappings_settings=mapping_settings,
            workspace_id=self.__workspace_id
        )

        workspace_settings = self.__workspace_general_settings

        old_coa = set(pre_save_general_settings.charts_of_accounts or [])
        new_coa = set(workspace_settings['charts_of_accounts'] or [])

        if workspace_settings['import_categories'] and old_coa != new_coa:
            ImportLog.objects.filter(workspace_id=self.__workspace_id, attribute_type='CATEGORY').update(last_successful_run_at=None, updated_at=datetime.now(timezone.utc))

    def post_save_mapping_settings(self, workspace_general_settings_instance: WorkspaceGeneralSettings):
        """
        Post save actions for mapping settings
        """
        destination_fields = []
        for setting in self.__mapping_settings:
            destination_fields.append(setting['destination_field'])

        MappingSetting.objects.filter(~Q(destination_field__in=destination_fields), destination_field__in=['CLASS', 'CUSTOMER', 'DEPARTMENT', 'TAX_CODE'], workspace_id=self.__workspace_id).delete()

        self.__update_expense_group_settings_for_departments()

        new_schedule_or_delete_fyle_import_tasks(workspace_general_settings_instance, self.__mapping_settings)
