import os
from datetime import datetime,timezone
import pytest
from fyle_rest_auth.models import User,AuthToken
from rest_framework.test import APIClient
from fyle.platform import Platform
from apps.fyle.helpers import get_access_token
from apps.workspaces.models import QBOCredential, FyleCredential
from fyle_qbo_api.tests import settings

def pytest_configure():
    os.system('sh ./tests/sql_fixtures/reset_db_fixtures/reset_db.sh')

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture()
def test_connection(db):
    """
    Creates a connection with Fyle
    """
    client_id = settings.FYLE_CLIENT_ID
    client_secret = settings.FYLE_CLIENT_SECRET
    token_url = settings.FYLE_TOKEN_URI
    refresh_token = settings.FYLE_REFRESH_TOKEN
    server_url = settings.FYLE_SERVER_URL

    fyle_connection = Platform(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        server_url=server_url
    )

    access_token = get_access_token(refresh_token)
    fyle_connection.access_token = access_token
    user_profile = fyle_connection.v1beta.spender.my_profile.get()['data']
    user = User(
        password='', last_login=datetime.now(tz=timezone.utc), id=1, email=user_profile['user']['email'],
        user_id=user_profile['user_id'], full_name='', active='t', staff='f', admin='t'
    )

    user.save()

    auth_token = AuthToken(
        id=1,
        refresh_token=refresh_token,
        user=user
    )
    auth_token.save()

    return fyle_connection


@pytest.fixture()
def add_qbo_credentials(db):

    workspaces = [8,9]
    QBOCredential.objects.create(
        workspace_id=workspaces[0],
        refresh_token = '',
        realm_id = '4620816365031245740',
        company_name = 'Sandbox Company_US_2',
        country = 'US',
        created_at = datetime.now(tz=timezone.utc),
        updated_at = datetime.now(tz=timezone.utc),
    )

    QBOCredential.objects.create(
        workspace_id=workspaces[1],
        refresh_token = '',
        realm_id = '4620816365071123640',
        company_name = 'Sandbox Company_US_4',
        country = 'US',
        created_at = datetime.now(tz=timezone.utc),
        updated_at = datetime.now(tz=timezone.utc),
    )

@pytest.fixture()
def add_fyle_credentials(db):
    workspaces = [8,9]

    for workspace_id in workspaces:
        FyleCredential.objects.create(
            refresh_token=settings.FYLE_REFRESH_TOKEN,
            workspace_id=workspace_id,
            cluster_domain='https://staging.fyle.tech'
        )