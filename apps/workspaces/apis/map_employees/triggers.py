from apps.mappings.queues import schedule_auto_map_employees
from apps.workspaces.models import WorkspaceGeneralSettings


class MapEmployeesTriggers:
    """
    Class containing all triggers for map_employees
    """

    @staticmethod
    def run_workspace_general_settings_triggers(workspace_general_settings_instance: WorkspaceGeneralSettings):
        """
        Run workspace general settings triggers
        """
        schedule_auto_map_employees(workspace_general_settings_instance.auto_map_employees, workspace_general_settings_instance.workspace.id)
