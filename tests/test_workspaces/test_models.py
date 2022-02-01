import pytest
from apps.workspaces.models import Workspace
from fyle_rest_auth.models import User
from datetime import datetime, timezone

@pytest.mark.django_db
def test_workspace_creation():
    """
    Test post of workspace
    """

    user = User.objects.get(id=1)

    new_workspace = Workspace.objects.create(
        id = 101,
        name = 'Fyle for labhvam',
        fyle_org_id = 'l@bhv@m',
        qbo_realm_id = '4620816365009870170',
        cluster_domain = None,
        last_synced_at = None,
        source_synced_at = None,
        destination_synced_at = None,
        created_at = datetime.now(tz=timezone.utc),
        updated_at = datetime.now(tz=timezone.utc)
    )

    new_workspace.user.add(user)

    workspace = Workspace.objects.get(id=101)

    assert workspace.name == 'Fyle for labhvam'
    assert workspace.fyle_org_id == 'l@bhv@m'

@pytest.mark.django_db
def test_get_of_workspace(add_workspace_to_database):
    """
    Test get of workspace
    """

    workspace = Workspace.objects.filter(name='Fyle for labhvam2').first()

    assert workspace.fyle_org_id == 'l@bhv@m2'
