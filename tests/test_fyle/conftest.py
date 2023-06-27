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
        name="Fyle for Testing",
        fyle_org_id="Testing",
        fyle_currency="USD",
        qbo_realm_id="4620816365007870291",
        cluster_domain=None,
        last_synced_at=None,
        source_synced_at=None,
        destination_synced_at=None,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )

    workspace.save()

    ExpenseGroupSettings.objects.create(
        reimbursable_expense_group_fields="{employee_email,report_id,claim_number,fund_source}",
        corporate_credit_card_expense_group_fields="{fund_source,employee_email,claim_number,expense_id,report_id}",
        expense_state="PAYMENT PROCESSING",
        ccc_expense_state="PAID",
        workspace_id=98,
        import_card_credits=False,
    )
