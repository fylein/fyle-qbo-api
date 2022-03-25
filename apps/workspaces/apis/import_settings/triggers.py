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
    def __init__(self, workspace_general_settings, mapping_settings, workspace_id):
        self.__workspace_general_settings = workspace_general_settings
        self.__mapping_settings = mapping_settings
        self.__workspace_id = workspace_id
    
    def __update_expense_group_settings_for_departments(self):
        """
        Should group expenses by department source field in case the export is journal entries
        """
        workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.__workspace_id).first()
        expense_group_settings = ExpenseGroupSettings.objects.get(
            workspace_id=self.__workspace_id
        )

    def post_save_workspace_general_settings(self):
        """
        Post save action for workspace general settings
        """
        schedule_tax_groups_creation(
            import_tax_codes=self.__workspace_general_settings.import_tax_codes,
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
