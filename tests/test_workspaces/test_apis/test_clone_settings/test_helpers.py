from fyle_rest_auth.models import User

from apps.workspaces.apis.clone_settings.helpers import get_latest_workspace


def test_get_latest_workspace(test_connection):
    
    user = User.objects.all().first()
    latest_workspace = get_latest_workspace(user.user_id)
        
    assert latest_workspace.fyle_org_id == 'fyle_org_id_dummy'
    assert latest_workspace.name  == 'Test Workspace 2'
