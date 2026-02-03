from datetime import datetime, timezone
from unittest import mock

import pytest
from fyle.platform import Platform
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute
from fyle_rest_auth.models import AuthToken, User
from rest_framework.test import APIClient

from apps.fyle.helpers import get_access_token
from apps.fyle.models import ExpenseFilter, ExpenseGroupSettings
from apps.workspaces.models import LastExportDetail, Workspace, WorkspaceGeneralSettings
from fyle_qbo_api.tests import settings
from tests.test_workspaces.fixtures import data as fyle_data


@pytest.fixture(autouse=True)
def mock_rabbitmq():
    with mock.patch('workers.helpers.RabbitMQConnection.get_instance') as mock_rabbitmq:
        mock_instance = mock.Mock()
        mock_instance.publish.return_value = None
        mock_instance.connect.return_value = None
        mock_rabbitmq.return_value = mock_instance
        yield mock_rabbitmq


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

    fyle_connection = Platform(token_url=token_url, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, server_url=server_url)

    access_token = get_access_token(refresh_token)
    fyle_connection.access_token = access_token
    user_profile = fyle_connection.v1.spender.my_profile.get()['data']
    user = User(password='', last_login=datetime.now(tz=timezone.utc), id=1, email=user_profile['user']['email'], user_id=user_profile['user_id'], full_name='', active='t', staff='f', admin='t')

    user.save()

    auth_token = AuthToken(id=1, refresh_token=refresh_token, user=user)
    auth_token.save()

    workspace = Workspace.objects.create(
        name='Test Workspace 2',
        fyle_org_id='fyle_org_id_dummy',
        fyle_currency='USD',
        app_version='v2',
        onboarding_state='COMPLETE'
    )
    workspace.user.add(user)
    LastExportDetail.objects.update_or_create(workspace=workspace)
    WorkspaceGeneralSettings.objects.create(
        workspace=workspace,
        reimbursable_expenses_object='BILL'
    )
    ExpenseGroupSettings.objects.create(workspace=workspace)

    return fyle_connection


@pytest.fixture(scope="session", autouse=True)
def default_session_fixture(request):
    patched_1 = mock.patch('qbosdk.QuickbooksOnlineSDK.update_access_token')
    patched_1.__enter__()

    patched_2 = mock.patch('fyle_rest_auth.authentication.get_fyle_admin', return_value=fyle_data['admin_user'])
    patched_2.__enter__()

    patched_3 = mock.patch('fyle.platform.internals.auth.Auth.update_access_token', return_value='asnfal.snkflanskfl.ansfklsan')
    patched_3.__enter__()

    patched_4 = mock.patch('apps.fyle.helpers.post_request', return_value={'access_token': 'easnfkjo12233.asnfaosnfa.absfjoabsfjk', 'cluster_domain': 'https://staging.fyle.tech'})
    patched_4.__enter__()

    patched_5 = mock.patch('fyle.platform.apis.v1.spender.MyProfile.get', return_value=fyle_data['admin_user'])
    patched_5.__enter__()


@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_expense_destination_attributes_1():
    """
    Pytest fixture to add expense & destination attributes to a workspace
    """
    values = ['Internet','Meals']
    count = 0

    for value in values:
        count += 1
        ExpenseAttribute.objects.create(
            workspace_id=1,
            attribute_type='CATEGORY',
            display_name='Category',
            value= value,
            source_id='1009{0}'.format(count),
            detail='Merchant - Platform APIs, Id - 1008',
            active=True
        )
        DestinationAttribute.objects.create(
            workspace_id=1,
            attribute_type='ACCOUNT',
            display_name='Account',
            value= value,
            destination_id=value,
            detail='Merchant - Platform APIs, Id - 10081',
            active=True
        )


@pytest.fixture()
@pytest.mark.django_db(databases=['default'])
def add_expense_destination_attributes_3():
    ExpenseAttribute.objects.create(
        workspace_id=1,
        attribute_type='CATEGORY',
        display_name='Category',
        value="123: QBO",
        source_id='10095',
        detail='Merchant - Platform APIs, Id - 10085',
        active=True
    )

    DestinationAttribute.objects.create(
        workspace_id=1,
        attribute_type='ACCOUNT',
        display_name='Account',
        value="QBO",
        destination_id='10085',
        detail='Merchant - Platform APIs, Id - 10085',
        active=True,
        code='123'
    )


@pytest.fixture()
def add_expense_filter(db):
    """
    Fixture to create an ExpenseFilter for testing skip export rules
    """
    expense_filter, _ = ExpenseFilter.objects.get_or_create(
        workspace_id=1,
        rank=1,
        defaults={
            'condition': 'employee_email',
            'operator': 'iexact',
            'values': ['test@test.com']
        }
    )
    return expense_filter
