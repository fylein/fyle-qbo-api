import pytest
from apps.workspaces.apis.export_settings.triggers import ExportSettingsTrigger
from apps.workspaces.models import WorkspaceGeneralSettings

def test_post_save_workspace_general_settings_export_trigger(mocker, db):
    workspace_general_setting = WorkspaceGeneralSettings.objects.filter(workspace_id=5).first()
    export_trigger = ExportSettingsTrigger(workspace_general_setting,5)

    workspace_general_setting.reimbursable_expenses_object = 'JOURNAL ENTRY'
    workspace_general_setting.corporate_credit_card_expenses_object = 'JOURNAL ENTRY'
    workspace_general_setting.import_items = True
    workspace_general_setting.save()

    export_trigger.post_save_workspace_general_settings(workspace_general_setting)

    assert workspace_general_setting.import_items == False