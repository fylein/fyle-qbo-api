from datetime import datetime, timezone

import pytest
from django.core.cache import cache
from fyle_rest_auth.models import User

from apps.workspaces.models import (
    FeatureConfig,
    LastExportDetail,
    Workspace,
    get_default_chart_of_accounts,
    get_default_memo_fields,
)


@pytest.mark.django_db
def test_workspace_creation():
    """
    Test post of workspace
    """

    user = User.objects.get(id=1)

    new_workspace = Workspace.objects.create(
        id=101,
        name='Fyle for labhvam',
        fyle_org_id='l@bhv@m',
        qbo_realm_id='4620816365009870170',
        cluster_domain=None,
        last_synced_at=None,
        source_synced_at=None,
        destination_synced_at=None,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )

    new_workspace.user.add(user)

    workspace = Workspace.objects.get(id=101)

    LastExportDetail.objects.create(workspace=workspace)

    assert workspace.name == 'Fyle for labhvam'
    assert workspace.fyle_org_id == 'l@bhv@m'


@pytest.mark.django_db
def test_get_of_workspace(add_workspace_to_database):
    """
    Test get of workspace
    """

    workspace = Workspace.objects.filter(name='Fyle for labhvam2').first()

    assert workspace.fyle_org_id == 'l@bhv@m2'


def test_get_default_chart_of_accounts():
    expected_accounts = ['Expense']
    actual_accounts = get_default_chart_of_accounts()
    assert actual_accounts == expected_accounts


def test_get_default_memo_fields():
    expected_fields = ['employee_email', 'category', 'spent_on', 'report_number', 'purpose', 'expense_link']
    actual_fields = get_default_memo_fields()
    assert actual_fields == expected_fields


@pytest.mark.django_db
def test_feature_config_get_feature_config():
    """Test FeatureConfig.get_feature_config() method with caching"""
    workspace = Workspace.objects.create(
        name='Test Workspace',
        fyle_org_id='test_org_fc'
    )
    FeatureConfig.objects.create(
        workspace_id=workspace.id,
        export_via_rabbitmq=True,
        import_via_rabbitmq=False,
        fyle_webhook_sync_enabled=True
    )
    result = FeatureConfig.get_feature_config(workspace.id, 'export_via_rabbitmq')
    assert result is True
    result = FeatureConfig.get_feature_config(workspace.id, 'export_via_rabbitmq')
    assert result is True
    result = FeatureConfig.get_feature_config(workspace.id, 'import_via_rabbitmq')
    assert result is False
    result = FeatureConfig.get_feature_config(workspace.id, 'fyle_webhook_sync_enabled')
    assert result is True
    cache.clear()
