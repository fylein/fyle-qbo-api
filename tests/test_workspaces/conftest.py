import pytest
from apps.workspaces.models import Workspace
from datetime import datetime, timezone


@pytest.fixture
def add_workspace_to_database():
    """
    Add worksapce to database fixture
    """
    workspace = Workspace.objects.create(
        id=100,
        name='Fyle for labhvam2',
        fyle_org_id='l@bhv@m2',
        qbo_realm_id='4620816365007870170',
        cluster_domain=None,
        last_synced_at=None,
        source_synced_at=None,
        destination_synced_at=None,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc)
    )

    workspace.save()
