from datetime import datetime, timezone
from unittest import mock

import pytest
from fyle.platform import Platform
from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_rest_auth.models import AuthToken, User
from rest_framework.test import APIClient

from apps.fyle.helpers import get_access_token
from apps.fyle.models import Expense, ExpenseGroupSettings, WorkspaceGeneralSettings
from apps.workspaces.models import FyleCredential, Workspace
from fyle_qbo_api.tests import settings
from tests.test_fyle.fixtures import data as fyle_fixtures
from tests.test_workspaces.fixtures import data as fyle_data


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
    refresh_token = "Dummy.Refresh.Token"
    server_url = settings.FYLE_SERVER_URL

    fyle_connection = Platform(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        server_url=server_url,
    )

    access_token = get_access_token(refresh_token)
    fyle_connection.access_token = access_token
    user_profile = fyle_connection.v1beta.spender.my_profile.get()["data"]
    print("Profile User", user_profile["user"]["email"])
    user = User(
        password="",
        last_login=datetime.now(tz=timezone.utc),
        id=1,
        email=user_profile["user"]["email"],
        user_id=user_profile["user_id"],
        full_name="",
        active="t",
        staff="f",
        admin="t",
    )

    user.save()

    auth_token = AuthToken(id=1, refresh_token=refresh_token, user=user)
    auth_token.save()

    return fyle_connection


@pytest.fixture(scope="session", autouse=True)
def default_session_fixture(request):
    patched_1 = mock.patch("qbosdk.QuickbooksOnlineSDK.update_access_token")
    patched_1.__enter__()

    patched_2 = mock.patch(
        "fyle_rest_auth.authentication.get_fyle_admin",
        return_value=fyle_data["admin_user"],
    )
    patched_2.__enter__()

    patched_3 = mock.patch(
        "fyle.platform.internals.auth.Auth.update_access_token",
        return_value="asnfal.snkflanskfl.ansfklsan",
    )
    patched_3.__enter__()

    patched_4 = mock.patch(
        "apps.fyle.helpers.post_request",
        return_value={
            "access_token": "easnfkjo12233.asnfaosnfa.absfjoabsfjk",
            "cluster_domain": "https://staging.fyle.tech",
        },
    )
    patched_4.__enter__()

    patched_5 = mock.patch(
        "fyle.platform.apis.v1beta.spender.MyProfile.get",
        return_value=fyle_data["admin_user"],
    )
    patched_5.__enter__()

    def unpatch():
        patched_1.__exit__()
        patched_2.__exit__()
        patched_3.__exit__()
        patched_4.__exit__()
        patched_5.__exit__()

    request.addfinalizer(unpatch)


@pytest.fixture()
def create_temp_workspace():
    workspace_ids = [1, 2, 3]
    # user = User.objects.get(email='ashwin.t@fyle.in')
    user = User(
        password="",
        last_login=datetime.now(tz=timezone.utc),
        id=1,
        email="ashwin.t@fyle.in",
        user_id="usqywo0f3nBY",
        full_name="",
        active="t",
        staff="f",
        admin="t",
    )

    user.save()
    auth_token = AuthToken(id=1, refresh_token="assist", user=user)
    auth_token.save()
    for workspace_id in workspace_ids:
        instance = Workspace.objects.create(
            id=workspace_id,
            name="Fyle For Testing {}".format(workspace_id),
            fyle_org_id="riseabovehate{}".format(workspace_id),
            fyle_currency="USD",
            qbo_realm_id="4620816365007870291",
            cluster_domain="https://dummy_cluster_domain.com",
            last_synced_at=None,
            source_synced_at=None,
            destination_synced_at=None,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        instance.user.add(user)
        ExpenseGroupSettings.objects.create(
            reimbursable_expense_group_fields="{employee_email,claim_number,fund_source,report_id}",  # noqa: E501
            corporate_credit_card_expense_group_fields="{employee_email,claim_number,fund_source,spent_at,report_id}",  # noqa: E501
            expense_state="PAYMENT PROCESSING",
            ccc_expense_state="APPROVED",
            ccc_export_date_type="spent_at",
            reimbursable_export_date_type="current_date",
            workspace_id=workspace_id,
            import_card_credits=False,
        )
        WorkspaceGeneralSettings.objects.create(
            reimbursable_expenses_object="EXPENSE",
            corporate_credit_card_expenses_object="CREDIT CARD PURCHASE",
            employee_field_mapping="VENDOR",
            import_projects=False,
            import_categories=False,
            sync_fyle_to_qbo_payments=True,
            sync_qbo_to_fyle_payments=False,
            auto_map_employees="Name",
            category_sync_version="v2",
            auto_create_destination_entity=True,
            map_merchant_to_vendor=True,
            je_single_credit_line=False,
            change_accounting_period=True,
            workspace_id=workspace_id,
            import_tax_codes=False,
            charts_of_accounts="{Expense}",
            memo_structure="{employee_email,category,spent_on,report_number,purpose,expense_link}",
            map_fyle_cards_qbo_account=True,
            skip_cards_mapping=False,
            import_vendors_as_merchants=False,
            auto_create_merchants_as_vendors=False,
            is_simplify_report_closure_enabled=True,
            is_multi_currency_allowed=False,
            import_items=False,
        )
        # GeneralMapping.objects.create(
        #     default_ccc_account_name="Mastercard",
        #     default_ccc_account_id=41,
        #     workspace_id=workspace_id,
        #     accounts_payable_id=91,
        #     accounts_payable_name="Accounts Payable (A/P)",
        #     default_ccc_vendor_id=159,
        #     default_ccc_vendor_name="Fyle",
        #     bill_payment_account_id=131,
        #     bill_payment_account_name="Checking Debit Card",
        #     qbo_expense_account_id=131,
        #     qbo_expense_account_name="Checking Debit Card",
        #     default_debit_card_account_id=131,
        #     default_debit_card_account_name="Checking Debit Card",
        # )


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


@pytest.fixture()
@pytest.mark.django_db(databases=["default"])
def add_expense_attributes():
    """
    Pytest fixture to add fyle credentials to a workspace
    """
    workspace_ids = [1, 2, 3]
    for workspace_id in workspace_ids:
        attribute = {
            "attribute_type": "PROJECT",
            "value": "Fyle{}".format(workspace_id),
            "source_id": 1212 + workspace_id,
            "display_name": "fyle12{}".format(workspace_id),
        }
        ExpenseAttribute.create_or_update_expense_attribute(attribute, workspace_id)


@pytest.fixture()
@pytest.mark.django_db(databases=["default"])
def add_expenses():
    """
    Add Expense to a workspace
    """
    expenses = fyle_fixtures["expenses"]

    for workspace_id in [1, 2, 3]:
        for expense in expenses:
            expense["id"] = expense["id"] + str(workspace_id)

        Expense.create_expense_objects(expenses, workspace_id)
