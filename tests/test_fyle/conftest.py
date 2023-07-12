import pytest

from apps.workspaces.models import FyleCredential


@pytest.fixture()
@pytest.mark.django_db(databases=["default"])
def add_fyle_credentials():
    """
    Pytest fixture to add fyle credentials to a workspace
    """
    workspace_ids = [1, 2, 3]
    for workspace_id in workspace_ids:
        FyleCredential.objects.create(
            refresh_token="dummy_refresh_token",
            workspace_id=workspace_id,
            cluster_domain="https://dummy_cluster_domain.com",
        )
