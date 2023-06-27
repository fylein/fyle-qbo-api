from apps.fyle.models import _format_date, _group_expenses, get_default_ccc_expense_state
from apps.fyle.models import *
from .fixtures import data


def test_default_fields():
    expense_group_field = get_default_expense_group_fields()
    expense_state = get_default_expense_state()
    ccc_expense_state = get_default_ccc_expense_state()

    assert expense_group_field == ['employee_email', 'report_id', 'claim_number', 'fund_source']
    assert expense_state == 'PAYMENT_PROCESSING'
    assert ccc_expense_state == 'PAID'


def test_create_expense_objects(db):
    payload = data['expenses']
    Expense.create_expense_objects(payload, 3)

    expense = Expense.objects.last()
    assert expense.expense_id == 'txLAP0oIB5Yb'


def test_expense_group_settings(create_temp_workspace, db):
    payload = data['expense_group_settings_payload']

    ExpenseGroupSettings.update_expense_group_settings(
        payload, 98
    )

    settings = ExpenseGroupSettings.objects.last()

    assert settings.expense_state == 'PAID'
    assert settings.ccc_export_date_type == 'spent_at'
    assert settings.ccc_expense_state == 'PAID'


def test_create_reimbursement(db):

    reimbursements = data['reimbursements']

    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=1)

    pending_reimbursement = Reimbursement.objects.get(reimbursement_id='reimgCW1Og0BcM')

    pending_reimbursement.state = 'PENDING'
    pending_reimbursement.settlement_id = 'setgCxsr2vTmZ'

    reimbursements[0]['is_paid'] = True

    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=1)

    paid_reimbursement = Reimbursement.objects.get(reimbursement_id='reimgCW1Og0BcM')
    paid_reimbursement.state == 'PAID'


def test_create_expense_groups_by_report_id_fund_source(db):
    workspace_id = 4
    payload = data['expenses']
    Expense.create_expense_objects(payload, workspace_id)
    expense_objects = Expense.objects.last()

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.reimbursable_export_date_type = 'last_spent_at'
    expense_group_settings.ccc_export_date_type = 'last_spent_at'
    expense_group_settings.save()

    field = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').last()
    field.attribute_type = 'KILLUA'
    field.save()

    expenses = Expense.objects.filter(id=33).all()

    expense_groups = _group_expenses(expenses, ['claim_number', 'fund_source', 'project', 'employee_email', 'report_id', 'Killua'], 4)
    assert expense_groups == [{'claim_number': 'C/2022/05/R/6', 'fund_source': 'PERSONAL', 'project': 'Bebe Rexha', 'employee_email': 'sravan.kumar@fyle.in', 'report_id': 'rpawE81idoYo', 'killua': '', 'total': 1, 'expense_ids': [33]}]

    expense_groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source([expense_objects], workspace_id)
    assert len(expense_groups) == 1

    expense_groups = ExpenseGroup.objects.last()
    assert expense_groups.exported_at is None

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    general_settings.reimbursable_expenses_object = 'BILL'
    general_settings.save()

    expenses = expense_groups.expenses.all()
    for expense in expenses:
        if expense.amount > 50:
            expense.amount = -100
        expense.save()

    ExpenseGroup.create_expense_groups_by_report_id_fund_source([expense_objects], workspace_id)

    expense_groups = ExpenseGroup.objects.last()
    assert expense_groups.exported_at is None


def test_format_date():
    date_string = _format_date('2022-05-13T09:32:06.643941Z')

    assert date_string == parser.parse('2022-05-13T09:32:06.643941Z')
