from apps.fyle.models import ExpenseGroupSettings
from apps.mappings.models import GeneralMapping
from apps.workspaces.models import WorkspaceGeneralSettings


class ExportSettingsTriggers:
    """
    Class containing all triggers for export_settings
    """
    @staticmethod
    def run_workspace_general_settings_triggers(workspace_general_settings_instance: WorkspaceGeneralSettings):
        """
        POST
        """
        print(workspace_general_settings_instance)

    @staticmethod
    def run_expense_group_settings_triggers(expense_group_settings_instance: ExpenseGroupSettings):
        print(expense_group_settings_instance)

    @staticmethod
    def run_general_mappings_triggers(general_mappings_instance: GeneralMapping):
        print(general_mappings_instance)
