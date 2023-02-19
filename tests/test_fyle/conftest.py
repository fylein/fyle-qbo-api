from datetime import datetime, timezone
import pytest
from apps.fyle.models import ExpenseGroupSettings
from apps.workspaces.models import Workspace, FyleCredential
from fyle.platform import Platform
from fyle_rest_auth.models import AuthToken, User
from apps.fyle.helpers import get_access_token
from fyle_qbo_api.tests import settings


@pytest.fixture
def create_temp_workspace(db):

    workspace = Workspace.objects.create(
        id=98,
        name = 'Fyle for Testing',
        fyle_org_id = 'Testing',
        fyle_currency = 'USD',
        qbo_realm_id = '4620816365007870291',
        cluster_domain = None,
        last_synced_at = None,
        source_synced_at = None,
        destination_synced_at = None,
        created_at = datetime.now(tz=timezone.utc),
        updated_at = datetime.now(tz=timezone.utc)
    )

    workspace.save()
    
    ExpenseGroupSettings.objects.create(
        reimbursable_expense_group_fields='{employee_email,report_id,claim_number,fund_source}',
        corporate_credit_card_expense_group_fields='{fund_source,employee_email,claim_number,expense_id,report_id}',
        expense_state='PAYMENT PROCESSING',
        ccc_expense_state='PAID',
        workspace_id=98,
        import_card_credits=False
    )


@pytest.fixture()
def add_fyle_credentials(db):
    workspace_id = 1

    FyleCredential.objects.create(
        refresh_token=settings.FYLE_REFRESH_TOKEN,
        workspace_id=workspace_id,
        cluster_domain='https://staging.fyle.tech'
    )


@pytest.fixture()
def access_token(db):
    """
    Creates a connection with Fyle
    """

    client_id = settings.FYLE_CLIENT_ID
    client_secret = settings.FYLE_CLIENT_SECRET
    token_url = settings.FYLE_TOKEN_URI
    refresh_token = settings.FYLE_REFRESH_TOKEN
    final_access_token = get_access_token(refresh_token=refresh_token)

    fyle = Platform(
        server_url="https://staging.fyle.tech/platform/v1beta",
        token_url=token_url,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret
    )

    user_profile = fyle.v1beta.spender.my_profile.get()['data']['user']
    user = User(
        password='', last_login=datetime.now(tz=timezone.utc), id=1, email=user_profile['email'],
        user_id=user_profile['id'], full_name='', active='t', staff='f', admin='t'
    )

    user.save()

    auth_token = AuthToken(
        id=1,
        refresh_token=refresh_token,
        user=user
    )
    auth_token.save()

    return final_access_token