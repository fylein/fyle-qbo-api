from datetime import datetime, timezone

from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
import pytest
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute

from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import LastExportDetail, Workspace, WorkspaceGeneralSettings


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


@pytest.fixture()
def setup_test_data_for_export_settings(add_workspace_with_settings):
    """
    Setup common test data for export settings tests
    """
    def _setup_data(workspace_id: int, config: dict = None):
        add_workspace_with_settings(workspace_id)

        if config:
            WorkspaceGeneralSettings.objects.update_or_create(
                workspace_id=workspace_id,
                defaults=config
            )

        TaskLog.objects.create(
            workspace_id=workspace_id,
            status='ENQUEUED',
            type='CREATING_EXPENSE'
        )

        return workspace_id

    return _setup_data


@pytest.fixture()
def create_expense_groups():
    """
    Create expense groups for testing
    """
    def _create_groups(workspace_id: int, group_configs: list):
        expense_groups = []
        for config in group_configs:
            expense_group = ExpenseGroup.objects.create(
                id=config.get('id'),
                workspace_id=workspace_id,
                fund_source=config.get('fund_source', 'PERSONAL'),
                exported_at=config.get('exported_at')
            )
            expense_groups.append(expense_group)
        return expense_groups

    return _create_groups


@pytest.fixture()
def create_mapping_errors():
    """
    Create mapping errors for testing
    """
    def _create_errors(workspace_id: int, error_configs: list):
        errors = []
        for config in error_configs:
            expense_attribute = None
            if config.get('attribute_type'):
                expense_attribute = ExpenseAttribute.objects.create(
                    workspace_id=workspace_id,
                    attribute_type=config['attribute_type'],
                    display_name=config.get('display_name', config['attribute_type'].title()),
                    value=config.get('value', f'test.{config["attribute_type"].lower()}@example.com')
                )

            error = Error.objects.create(
                workspace_id=workspace_id,
                type=config.get('type', 'EMPLOYEE_MAPPING'),
                expense_attribute=expense_attribute,
                mapping_error_expense_group_ids=config.get('mapping_error_expense_group_ids', []),
                error_title=config.get('error_title', 'Test Error'),
                error_detail=config.get('error_detail', 'Test error detail'),
                is_resolved=config.get('is_resolved', False),
                expense_group_id=config.get('expense_group_id')
            )
            errors.append(error)
        return errors

    return _create_errors


@pytest.fixture()
def create_task_logs():
    """
    Create task logs for testing
    """
    def _create_logs(workspace_id: int, log_configs: list):
        task_logs = []
        for config in log_configs:
            task_log = TaskLog.objects.create(
                workspace_id=workspace_id,
                expense_group_id=config.get('expense_group_id'),
                status=config.get('status', 'ENQUEUED'),
                type=config.get('type', 'CREATING_EXPENSE')
            )
            task_logs.append(task_log)
        return task_logs

    return _create_logs
