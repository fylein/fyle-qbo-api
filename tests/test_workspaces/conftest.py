from datetime import datetime, timezone

from apps.fyle.models import ExpenseGroupSettings
import pytest
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute

from apps.workspaces.models import LastExportDetail, Workspace


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

    LastExportDetail.objects.update_or_create(workspace=workspace)


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


@pytest.fixture
def add_expense_attributes_for_unmapped_cards_test():
    """
    Add ExpenseAttribute test data for run_post_configration_triggers signal test
    """
    workspace_id = 1

    ExpenseAttribute.objects.get_or_create(
        attribute_type='CORPORATE_CARD',
        workspace_id=workspace_id,
        display_name='Test Card 1',
        value='card1',
        source_id='card1',
        defaults={'active': True}
    )
    ExpenseAttribute.objects.get_or_create(
        attribute_type='CORPORATE_CARD',
        workspace_id=workspace_id,
        display_name='Test Card 2',
        value='card2',
        source_id='card2',
        defaults={'active': True}
    )


@pytest.fixture()
def add_workspace_with_settings(db):
    """
    Add workspace with all required settings for export settings tests
    """
    def _create_workspace(workspace_id: int) -> int:
        Workspace.objects.update_or_create(
            id=workspace_id,
            defaults={
                'name': f'Test Workspace {workspace_id}',
                'fyle_org_id': f'fyle_org_{workspace_id}'
            }
        )
        LastExportDetail.objects.update_or_create(workspace_id=workspace_id)

        ExpenseGroupSettings.objects.update_or_create(
            workspace_id=workspace_id,
            defaults={
                'reimbursable_expense_group_fields': ['employee_email', 'report_id', 'claim_number', 'fund_source'],
                'corporate_credit_card_expense_group_fields': ['fund_source', 'employee_email', 'claim_number', 'expense_id', 'report_id'],
                'expense_state': 'PAYMENT_PROCESSING',
                'reimbursable_export_date_type': 'current_date',
                'ccc_export_date_type': 'current_date'
            }
        )
        return workspace_id

    return _create_workspace
