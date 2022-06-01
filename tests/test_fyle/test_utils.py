import pytest
from apps.fyle.helpers import get_fyle_orgs
from apps.workspaces.models import FyleCredential
from apps.fyle.utils import FyleConnector
from .fixtures import data


@pytest.mark.django_db()
def test_get_fyle_orgs():
    fyle_credentials = FyleCredential.objects.get(workspace_id=1)

    fyle_orgs = get_fyle_orgs(fyle_credentials.refresh_token, 'https://staging.fyle.tech')
    print(fyle_orgs)
    assert fyle_orgs[0] == data['fyle_orgs'][0]


@pytest.mark.django_db()
def test_get_attachments():

    fyle_credentials = FyleCredential.objects.get(workspace_id=3)
    fyle_connector = FyleConnector(fyle_credentials.refresh_token)

    attachment = fyle_connector.get_attachments(['tx4w7YXZV1fa'])
    assert attachment[0]['filename'] == 'Screenshot 2022-05-23 at 9.47.26 AM.png'

    attachment = fyle_connector.get_attachments(['tx4w7YXZV'])
    assert attachment == []