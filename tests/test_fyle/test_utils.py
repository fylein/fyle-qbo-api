import pytest
from apps.fyle.helpers import get_fyle_orgs
from apps.workspaces.models import FyleCredential
from fyle_integrations_platform_connector import PlatformConnector

from .fixtures import data


@pytest.mark.django_db()
def test_get_fyle_orgs():
    fyle_credentials = FyleCredential.objects.get(workspace_id=1)

    fyle_orgs = get_fyle_orgs(fyle_credentials.refresh_token, 'https://staging.fyle.tech')
    assert fyle_orgs[0] == data['fyle_orgs'][0]