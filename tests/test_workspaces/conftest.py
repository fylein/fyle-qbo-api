from datetime import datetime, timezone

import pytest
from fyle_accounting_mappings.models import DestinationAttribute

from apps.workspaces.models import Workspace


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
        updated_at=datetime.now(tz=timezone.utc),
    )

    workspace.save()


@pytest.fixture
def add_destination_attributes_for_import_items_test():
    """
    Add DestinationAttribute test data for pre_save_workspace_general_settings signal test
    """
    workspace_id = 1

    item_attribute_1 = DestinationAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='ACCOUNT',
        display_name='Item',
        value='Test Item 1',
        destination_id='item1',
        active=True
    )

    item_attribute_2 = DestinationAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='ACCOUNT',
        display_name='Item',
        value='Test Item 2',
        destination_id='item2',
        active=True
    )

    inactive_item_attribute = DestinationAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='ACCOUNT',
        display_name='Item',
        value='Inactive Item',
        destination_id='inactive_item',
        active=False
    )

    return {
        'item_attribute_1': item_attribute_1,
        'item_attribute_2': item_attribute_2,
        'inactive_item_attribute': inactive_item_attribute
    }
