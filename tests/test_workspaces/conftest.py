from datetime import datetime, timezone
from typing import Callable, Optional

from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
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


@pytest.fixture
def add_category_test_expense(db):
    """
    Create expense for category change tests
    """
    workspace = Workspace.objects.get(id=1)
    expense = Expense.objects.create(
        workspace_id=workspace.id,
        expense_id='txCategoryTest',
        employee_email='category.test@test.com',
        employee_name='Category Test User',
        category='Test Category',
        amount=100,
        currency='USD',
        org_id=workspace.fyle_org_id,
        settlement_id='setlCat',
        report_id='rpCat',
        spent_at='2024-01-01T00:00:00Z',
        expense_created_at='2024-01-01T00:00:00Z',
        expense_updated_at='2024-01-01T00:00:00Z',
        fund_source='PERSONAL'
    )
    return expense


@pytest.fixture
def add_category_test_expense_group(db, add_category_test_expense):
    """
    Create expense group for category change tests
    """
    workspace = Workspace.objects.get(id=1)
    expense = add_category_test_expense
    expense_group = ExpenseGroup.objects.create(
        workspace_id=workspace.id,
        fund_source='PERSONAL',
        description={'employee_email': expense.employee_email},
        employee_name=expense.employee_name
    )
    expense_group.expenses.add(expense)
    return expense_group


@pytest.fixture
def get_or_create_task_log(db) -> Callable:
    """
    Fixture to get or create a TaskLog for an expense group
    Returns a function that can be called with expense_group and optional parameters
    """
    def _get_or_create_task_log(
        expense_group: ExpenseGroup,
        task_type: str = 'FETCHING_EXPENSES',
        status: str = 'COMPLETE',
        updated_at: Optional[datetime] = None
    ) -> TaskLog:
        task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
        if not task_log:
            task_log = TaskLog.objects.create(
                expense_group_id=expense_group.id,
                workspace_id=expense_group.workspace_id,
                type=task_type,
                status=status,
                updated_at=updated_at
            )
        return task_log
    return _get_or_create_task_log


@pytest.fixture
def create_expense_group_expense(db):
    """
    Create expense group and expense for system comments tests
    """
    workspace = Workspace.objects.get(id=3)

    expense_group = ExpenseGroup.objects.create(
        workspace_id=3,
        fund_source='PERSONAL',
        description={'employee_email': 'test@fyle.in'}
    )

    expense, _ = Expense.objects.update_or_create(
        expense_id='tx_sys_comment_test',
        defaults={
            'workspace_id': workspace.id,
            'employee_email': 'test@fyle.in',
            'category': 'category',
            'sub_category': 'sub_category',
            'project': 'project',
            'expense_number': 'E/2024/01/T/1',
            'org_id': workspace.fyle_org_id,
            'claim_number': 'C/2024/01/R/1',
            'amount': 100.0,
            'currency': 'USD',
            'foreign_amount': 100.0,
            'foreign_currency': 'USD',
            'settlement_id': 'setl_test',
            'reimbursable': True,
            'billable': True,
            'state': 'APPROVED',
            'vendor': 'vendor',
            'cost_center': 'cost_center',
            'report_id': 'rp_test',
            'spent_at': datetime.now(tz=timezone.utc),
            'expense_created_at': datetime.now(tz=timezone.utc),
            'expense_updated_at': datetime.now(tz=timezone.utc),
            'fund_source': 'PERSONAL'
        }
    )

    expense_group.expenses.add(expense)

    return expense_group, expense
