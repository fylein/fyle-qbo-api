from typing import Dict

from apps.mappings.schedules import schedule_or_delete_fyle_import_tasks as new_schedule_or_delete_fyle_import_tasks
from apps.quickbooks_online.actions import update_last_export_details
from apps.workspaces.apis.export_settings.helpers import clear_workspace_errors_on_export_type_change
from apps.workspaces.models import LastExportDetail, WorkspaceGeneralSettings


class ExportSettingsTrigger:
    def __init__(self, workspace_general_settings: Dict, workspace_id: int, old_configurations: Dict):
        self.__workspace_general_settings = workspace_general_settings
        self.__workspace_id = workspace_id
        self.__old_configurations = old_configurations

    def post_save_workspace_general_settings(self):
        """
        Post save action for workspace general settings
        """

        workspace_general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.__workspace_id).first()

        if (self.__workspace_general_settings['reimbursable_expenses_object'] == 'JOURNAL ENTRY' or self.__workspace_general_settings['corporate_credit_card_expenses_object'] == 'JOURNAL ENTRY') and workspace_general_settings.import_items:

            # Disable category for items mapping and set import-items to flase
            workspace_general_settings.import_items = False
            workspace_general_settings.save()
            new_schedule_or_delete_fyle_import_tasks(workspace_general_settings)

        if self.__old_configurations and self.__workspace_general_settings:
            clear_workspace_errors_on_export_type_change(self.__workspace_id, self.__old_configurations, self.__workspace_general_settings)

            last_export_detail = LastExportDetail.objects.filter(workspace_id=self.__workspace_id).first()
            if last_export_detail and last_export_detail.last_exported_at:
                update_last_export_details(self.__workspace_id)
