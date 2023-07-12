from apps.mappings.queue import schedule_bill_payment_creation
from apps.quickbooks_online.queue import schedule_qbo_objects_status_sync, schedule_reimbursements_sync
from apps.workspaces.models import WorkspaceGeneralSettings


class AdvancedConfigurationsTriggers:
    """
    Class containing all triggers for advanced_configurations
    """

    @staticmethod
    def run_workspace_general_settings_triggers(workspace_general_settings_instance: WorkspaceGeneralSettings):
        """
        Run workspace general settings triggers
        """
        schedule_bill_payment_creation(sync_fyle_to_qbo_payments=workspace_general_settings_instance.sync_fyle_to_qbo_payments, workspace_id=workspace_general_settings_instance.workspace.id)

        schedule_qbo_objects_status_sync(sync_qbo_to_fyle_payments=workspace_general_settings_instance.sync_qbo_to_fyle_payments, workspace_id=workspace_general_settings_instance.workspace.id)

        schedule_reimbursements_sync(sync_qbo_to_fyle_payments=workspace_general_settings_instance.sync_qbo_to_fyle_payments, workspace_id=workspace_general_settings_instance.workspace.id)
