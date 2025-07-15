from apps.workspaces.helpers import enable_multi_currency_support
from apps.workspaces.models import QBOCredential, Workspace, WorkspaceGeneralSettings


def test_enable_multi_currency_support(mocker, db):
    """
    Test enable multi currency support
    """
    workspace_id = 5

    workspace_general_setting = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    workspace_general_setting.is_multi_currency_allowed = False
    workspace_general_setting.save()

    Workspace.objects.filter(id=workspace_id).update(fyle_currency='YOLO')
    QBOCredential.objects.filter(workspace_id=workspace_id).update(currency='USD')

    enable_multi_currency_support(workspace_general_settings=workspace_general_setting)

    workspace_general_setting = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    assert workspace_general_setting.is_multi_currency_allowed == True
