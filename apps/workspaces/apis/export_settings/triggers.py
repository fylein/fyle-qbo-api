from typing import Dict
from django_q.tasks import async_task

from apps.workspaces.models import WorkspaceGeneralSettings

class ExportSettingsTrigger:
    def __init__(self, workspace_general_settings: Dict, workspace_id: int):
        self.workspace_general_settings = workspace_general_settings
        self.workspace_id = workspace_id

    def post_save_workspace_general_settings(self, workspace_general_settings_instance: WorkspaceGeneralSettings):
        """
        Post save action for workspace general settings
        """

        if (workspace_general_settings_instance.reimbursable_expenses_object == 'JOURNAL ENTRY' or \
            workspace_general_settings_instance.corporate_credit_card_expenses_object == 'JOURNAL ENTRY') and\
            workspace_general_settings_instance.import_items:

            # Disable category for items mapping and set import-items to flase
            workspace_general_settings_instance.import_items = False
            workspace_general_settings_instance.save()
            async_task('apps.mappings.tasks.disable_category_for_items_mapping', workspace_general_settings_instance)
