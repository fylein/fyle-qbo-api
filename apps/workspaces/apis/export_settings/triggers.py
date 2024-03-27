from typing import Dict

from apps.mappings.schedules import schedule_or_delete_fyle_import_tasks as new_schedule_or_delete_fyle_import_tasks
from apps.workspaces.models import WorkspaceGeneralSettings, LastExportDetail
from apps.fyle.models import ExpenseGroup
from apps.tasks.models import TaskLog, Error
from apps.quickbooks_online.actions import update_last_export_details


class ExportSettingsTrigger:
    def __init__(self, workspace_general_settings: Dict, workspace_id: int):
        self.__workspace_general_settings = workspace_general_settings
        self.__workspace_id = workspace_id

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

        # Delete all the errors and task logs for disabled export type
        fund_source = []

        if self.__workspace_general_settings['reimbursable_expenses_object']:
            fund_source.append('PERSONAL')
        if self.__workspace_general_settings['corporate_credit_card_expenses_object']:
            fund_source.append('CCC')

        expense_group_ids = ExpenseGroup.objects.filter(
            workspace_id=self.__workspace_id,
            exported_at__isnull=True
        ).exclude(fund_source__in=fund_source).values_list('id', flat=True)

        if expense_group_ids:
            Error.objects.filter(workspace_id = self.__workspace_id, expense_group_id__in=expense_group_ids).delete()
            TaskLog.objects.filter(workspace_id = self.__workspace_id, expense_group_id__in=expense_group_ids, status__in=['FAILED', 'FATAL']).delete()
            last_export_detail = LastExportDetail.objects.filter(workspace_id=self.__workspace_id).first()
            if last_export_detail.last_exported_at:
                update_last_export_details(self.__workspace_id)
