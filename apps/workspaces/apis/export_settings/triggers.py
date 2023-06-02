from typing import Dict
from django_q.tasks import async_task

from apps.workspaces.models import WorkspaceGeneralSettings

class ExportSettingsTrigger:
    def __init__(self, workspace_general_settings: Dict, workspace_id: int):
        self.__workspace_general_settings = workspace_general_settings
        self.__workspace_id = workspace_id

    def post_save_workspace_general_settings(self):
        """
        Post save action for workspace general settings
        """

        workspace_general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.__workspace_id).first()

        if (self.__workspace_general_settings['reimbursable_expenses_object'] == 'JOURNAL ENTRY' or \
            self.__workspace_general_settings['corporate_credit_card_expenses_object'] == 'JOURNAL ENTRY') and\
            workspace_general_settings.import_items:

            # Disable category for items mapping and set import-items to flase
            workspace_general_settings.import_items = False
            workspace_general_settings.save()
            async_task('apps.mappings.tasks.disable_category_for_items_mapping', self.__workspace_id)
