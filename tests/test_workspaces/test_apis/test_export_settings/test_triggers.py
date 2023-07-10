from apps.workspaces.apis.export_settings.triggers import ExportSettingsTrigger
from apps.workspaces.models import WorkspaceGeneralSettings


def test_post_save_workspace_general_settings_export_trigger(mocker, db):
    # setting the import_items to True
    workspace_general_setting = WorkspaceGeneralSettings.objects.filter(
        workspace_id=5
    ).first()
    workspace_general_setting.import_items = True
    workspace_general_setting.save()

    # payload for the export trigger
    workspace_general_settings_payload = {
        "reimbursable_expenses_object": "JOURNAL ENTRY",
        "corporate_credit_card_expenses_object": "JOURNAL ENTRY",
    }
    workspace_id = 5

    export_trigger = ExportSettingsTrigger(
        workspace_general_settings=workspace_general_settings_payload,
        workspace_id=workspace_id,
    )
    export_trigger.post_save_workspace_general_settings()

    workspace_general_setting = WorkspaceGeneralSettings.objects.filter(
        workspace_id=5
    ).first()
    assert workspace_general_setting.import_items == False
