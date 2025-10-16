from datetime import datetime, timezone

import pytest

from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.workspaces.models import LastExportDetail, Workspace


@pytest.fixture
def create_temp_workspace(db):
    workspace = Workspace.objects.create(
        id=98,
        name='Fyle for Testing',
        fyle_org_id='Testing',
        fyle_currency='USD',
        qbo_realm_id='4620816365007870291',
        cluster_domain=None,
        last_synced_at=None,
        source_synced_at=None,
        destination_synced_at=None,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )

    workspace.save()

    ExpenseGroupSettings.objects.create(
        reimbursable_expense_group_fields='{employee_email,report_id,claim_number,fund_source}',
        corporate_credit_card_expense_group_fields='{fund_source,employee_email,claim_number,expense_id,report_id}',
        expense_state='PAYMENT PROCESSING',
        ccc_expense_state='PAID',
        workspace_id=98,
        import_card_credits=False,
    )

    LastExportDetail.objects.update_or_create(workspace=workspace)


@pytest.fixture
def add_expense_report_data(db):
    """
    Fixture to add expense and expense group data for workspace_id=3
    for testing expense report change handlers
    """
    # Create expenses for workspace 3
    expense1 = Expense.objects.create(
        workspace_id=3,
        expense_id='txExpense123',
        employee_email='user@example.com',
        employee_name='Test User',
        category='Food',
        sub_category='Food',
        project='Project 1',
        expense_number='E/2024/01/T/1',
        org_id='orTestOrg123',
        claim_number='C/2024/01/R/1',
        amount=100.0,
        currency='USD',
        foreign_amount=None,
        foreign_currency=None,
        settlement_id='setl123',
        reimbursable=True,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor='Test Vendor',
        cost_center='Cost Center 1',
        purpose='Test purpose',
        report_id='rpReport123',
        spent_at='2024-01-15T10:00:00.000Z',
        approved_at='2024-01-16T10:00:00.000Z',
        expense_created_at='2024-01-15T09:00:00.000Z',
        expense_updated_at='2024-01-16T09:00:00.000Z',
        fund_source='PERSONAL',
        verified_at='2024-01-16T10:00:00.000Z',
        custom_properties={},
        tax_amount=0,
        tax_group_id=None,
        corporate_card_id=None,
        is_skipped=False
    )

    expense2 = Expense.objects.create(
        workspace_id=3,
        expense_id='txExpense456',
        employee_email='user@example.com',
        employee_name='Test User',
        category='Travel',
        sub_category='Travel',
        project='Project 1',
        expense_number='E/2024/01/T/2',
        org_id='orTestOrg123',
        claim_number='C/2024/01/R/1',
        amount=200.0,
        currency='USD',
        foreign_amount=None,
        foreign_currency=None,
        settlement_id='setl123',
        reimbursable=True,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor='Test Vendor 2',
        cost_center='Cost Center 1',
        purpose='Test purpose 2',
        report_id='rpReport123',
        spent_at='2024-01-15T11:00:00.000Z',
        approved_at='2024-01-16T11:00:00.000Z',
        expense_created_at='2024-01-15T10:00:00.000Z',
        expense_updated_at='2024-01-16T10:00:00.000Z',
        fund_source='PERSONAL',
        verified_at='2024-01-16T11:00:00.000Z',
        custom_properties={},
        tax_amount=0,
        tax_group_id=None,
        corporate_card_id=None,
        is_skipped=False
    )

    # Create expense group for workspace 3
    expense_group = ExpenseGroup.objects.create(
        workspace_id=3,
        fund_source='PERSONAL',
        description={'claim_number': 'C/2024/01/R/1', 'employee_email': 'user@example.com'},
        employee_name='Test User',
        exported_at=None
    )

    # Add expenses to the group
    expense_group.expenses.add(expense1, expense2)

    return {
        'workspace_id': 3,
        'expenses': [expense1, expense2],
        'expense_group': expense_group
    }
