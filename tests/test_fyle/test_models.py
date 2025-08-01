from fyle_accounting_mappings.models import ExpenseAttribute

from apps.fyle.models import (
    Expense,
    ExpenseGroup,
    ExpenseGroupSettings,
    Reimbursement,
    Workspace,
    WorkspaceGeneralSettings,
    _format_date,
    _group_expenses,
    get_default_ccc_expense_state,
    get_default_expense_group_fields,
    get_default_expense_state,
    parser,
)
from tests.test_fyle.fixtures import data


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

    expense = Expense.objects.all().order_by('id').last()
    assert expense.expense_id == 'txLAP0oIB5Yb'


def test_expense_group_settings(create_temp_workspace, db):
    payload = data['expense_group_settings_payload']
    user = Workspace.objects.get(id=1).user

    ExpenseGroupSettings.update_expense_group_settings(payload, 98, user)

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


def test_create_expense_groups_by_report_id_fund_source_spent_at(db):
    expenses = data["expenses_spent_at"]

    expense_objects = Expense.create_expense_objects(expenses, 1)

    workspace = Workspace.objects.get(id=1)

    expense_group_setting = ExpenseGroupSettings.objects.get(workspace_id=1)
    expense_group_setting.reimbursable_export_date_type = "spent_at"
    reimbursable_expense_group_fields = (
        expense_group_setting.reimbursable_expense_group_fields
    )
    reimbursable_expense_group_fields.append("spent_at")
    expense_group_setting.reimbursable_expense_group_fields = (
        reimbursable_expense_group_fields
    )
    expense_group_setting.save()

    assert len(expense_objects) == 3

    ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, 1)

    expense_group = (
        ExpenseGroup.objects.filter(workspace=workspace).order_by("-created_at").first()
    )

    assert expense_group.expenses.count() == 2


def test_create_expense_groups_refund_invalid(db):

    workspace = Workspace.objects.get(id=1)
    configuration = WorkspaceGeneralSettings.objects.get(workspace=workspace)

    configuration.corporate_credit_card_expenses_object = "BILL"
    configuration.save()

    expenses = data["expense_refund_invalid"]
    expense_objects = Expense.create_expense_objects(expenses, 1)
    assert len(expense_objects) == 2
    ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, 1)
    expense_group = (
        ExpenseGroup.objects.filter(workspace=workspace).order_by("-created_at").first()
    )

    assert expense_group is None


def test_create_expense_groups_refund(db):
    expenses = data["expense_refund_valid"]
    expense_objects = Expense.create_expense_objects(expenses, 1)

    assert len(expense_objects) == 2
    workspace = workspace = Workspace.objects.get(id=1)
    configuration = WorkspaceGeneralSettings.objects.get(workspace=workspace)

    configuration.corporate_credit_card_expenses_object = "BILL"
    configuration.save()

    ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, 1)

    expense_group = (
        ExpenseGroup.objects.filter(workspace=workspace).order_by("-created_at").first()
    )
    assert expense_group.expenses.count() == 2


def creat_expense_groups_by_report_id_refund_spent_at(db):
    workspace = workspace = Workspace.objects.get(id=1)
    configuration = WorkspaceGeneralSettings.objects.get(workspace=workspace)

    configuration.corporate_credit_card_expenses_object = "BILL"
    configuration.save()

    expenses = data["expense_refund_spend_at"]

    expense_objects = Expense.create_expense_objects(expenses, 1)
    expense_group_setting = ExpenseGroupSettings.objects.get(workspace_id=1)
    expense_group_setting.ccc_export_date_type = "spent_at"
    corporate_expense_group_fields = (
        expense_group_setting.corporate_credit_card_expense_group_fields
    )
    corporate_expense_group_fields.append("spent_at")
    expense_group_setting.corporate_credit_card_expense_group_fields = (
        corporate_expense_group_fields
    )
    expense_group_setting.save()

    assert len(expense_objects) == 2

    ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, 1)

    expense_group = (
        ExpenseGroup.objects.filter(workspace=workspace).order_by("-created_at").first()
    )
    assert expense_group.expenses.count() == 1


def test_create_expense_group_report_id_journal_entry(db):

    workspace = workspace = Workspace.objects.get(id=1)
    configuration = WorkspaceGeneralSettings.objects.get(workspace=workspace)

    configuration.corporate_credit_card_expenses_object = "JOURNAL ENTRY"
    configuration.save()

    expense_group_setting = ExpenseGroupSettings.objects.get(workspace_id=1)

    corporate_expense_group_fields = (
        expense_group_setting.corporate_credit_card_expense_group_fields
    )
    corporate_expense_group_fields.append("expense_id")
    expense_group_setting.corporate_credit_card_expense_group_fields = (
        corporate_expense_group_fields
    )
    expense_group_setting.save()
    workspace = workspace = Workspace.objects.get(id=1)
    expenses = data["expense_refund_single_ccc"]
    expense_objects = Expense.create_expense_objects([expenses], 1)
    assert len(expense_objects) == 1
    ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, 1)
    expense_group = (
        ExpenseGroup.objects.filter(workspace=workspace).order_by("-created_at").first()
    )
    assert expense_group.expenses.count() == 1


def test_create_expense_group_report_id_check(db):

    workspace = workspace = Workspace.objects.get(id=1)
    configuration = WorkspaceGeneralSettings.objects.get(workspace=workspace)

    configuration.reimbursable_expenses_object = "CHECK"
    configuration.save()

    expense_group_setting = ExpenseGroupSettings.objects.get(workspace_id=1)

    reimbursable_expense_group_fields = (
        expense_group_setting.reimbursable_expense_group_fields
    )
    reimbursable_expense_group_fields.append("expense_id")
    expense_group_setting.reimbursable_expense_group_fields = (
        reimbursable_expense_group_fields
    )
    expense_group_setting.save()
    workspace = workspace = Workspace.objects.get(id=1)
    expenses = data["expense_refund_single"]
    expense_objects = Expense.create_expense_objects([expenses], 1)
    assert len(expense_objects) == 1
    ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, 1)
    expense_group = (
        ExpenseGroup.objects.filter(workspace=workspace).order_by("-created_at").first()
    )
    assert expense_group is None


def test_create_expense_group_report_id_expense_report(db):

    workspace = workspace = Workspace.objects.get(id=1)
    configuration = WorkspaceGeneralSettings.objects.get(workspace=workspace)

    configuration.reimbursable_expenses_object = "EXPENSE"
    configuration.save()

    expense_group_setting = ExpenseGroupSettings.objects.get(workspace_id=1)

    reimbursable_expense_group_fields = (
        expense_group_setting.reimbursable_expense_group_fields
    )
    reimbursable_expense_group_fields.append("expense_id")
    expense_group_setting.reimbursable_expense_group_fields = (
        reimbursable_expense_group_fields
    )
    expense_group_setting.save()
    workspace = workspace = Workspace.objects.get(id=1)
    expenses = data["expense_refund_single"]
    expense_objects = Expense.create_expense_objects([expenses], 1)
    assert len(expense_objects) == 1
    ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, 1)
    expense_group = (
        ExpenseGroup.objects.filter(workspace=workspace).order_by("-created_at").first()
    )
    assert expense_group is None


def test_create_expense_group_report_id_debit_card_expense(db):

    workspace = workspace = Workspace.objects.get(id=1)
    configuration = WorkspaceGeneralSettings.objects.get(workspace=workspace)

    configuration.corporate_credit_card_expenses_object = "DEBIT CARD EXPENSE"
    configuration.save()

    expense_group_setting = ExpenseGroupSettings.objects.get(workspace_id=1)

    corporate_expense_group_fields = (
        expense_group_setting.corporate_credit_card_expense_group_fields
    )
    corporate_expense_group_fields.append("expense_id")
    expense_group_setting.corporate_credit_card_expense_group_fields = (
        corporate_expense_group_fields
    )
    expense_group_setting.save()
    workspace = workspace = Workspace.objects.get(id=1)
    expenses = data["expense_refund_single_ccc"]
    expense_objects = Expense.create_expense_objects([expenses], 1)
    assert len(expense_objects) == 1
    ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, 1)
    expense_group = (
        ExpenseGroup.objects.filter(workspace=workspace).order_by("-created_at").first()
    )
    assert expense_group.expenses.count() == 1


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

    expense_groups, _ = ExpenseGroup.create_expense_groups_by_report_id_fund_source([expense_objects], workspace_id)
    assert len(expense_groups) == 1

    expense_groups = ExpenseGroup.objects.last()
    assert expense_groups.exported_at == None

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
    assert expense_groups.exported_at == None


def test_split_expenses_no_bank_transaction_id(db):
    # Grouping of expenses with no bank transaction id
    expenses = data['ccc_expenses_split_no_bank_transaction_id']
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=1)
    general_settings.corporate_credit_card_expenses_object = 'CREDIT CARD PURCHASE'
    general_settings.save()

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=1)
    expense_group_settings.ccc_export_date_type = 'last_spent_at'
    expense_group_settings.split_expense_grouping = 'SINGLE_LINE_ITEM'
    expense_group_settings.save()

    expense_objects = Expense.create_expense_objects(expenses, 1)
    assert len(expense_objects) == 2

    expense_groups = _group_expenses(expense_objects, ['expense_id', 'fund_source', 'employee_email', 'spent_at'], 4)
    assert len(expense_groups) == 2

    expense_group_settings.split_expense_grouping = 'MULTIPLE_LINE_ITEM'
    expense_group_settings.save()

    expense_groups = _group_expenses(expense_objects, ['expense_id', 'fund_source', 'employee_email', 'spent_at'], 4)
    assert len(expense_groups) == 2


def test_split_expenses_same_bank_transaction_id(db):
    # Grouping of expenses with same bank transaction id
    expenses = data['ccc_expenses_split_same_bank_transaction_id']
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=1)
    general_settings.corporate_credit_card_expenses_object = 'CREDIT CARD PURCHASE'
    general_settings.save()

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=1)
    expense_group_settings.ccc_export_date_type = 'last_spent_at'
    expense_group_settings.split_expense_grouping = 'SINGLE_LINE_ITEM'
    expense_group_settings.save()

    expense_objects = Expense.create_expense_objects(expenses, 1)
    assert len(expense_objects) == 2

    expense_groups = _group_expenses(expense_objects, ['expense_id', 'fund_source', 'employee_email', 'spent_at'], 4)
    assert len(expense_groups) == 2

    expense_group_settings.split_expense_grouping = 'MULTIPLE_LINE_ITEM'
    expense_group_settings.save()

    expense_groups = _group_expenses(expense_objects, ['expense_id', 'fund_source', 'employee_email', 'spent_at'], 4)
    assert len(expense_groups) == 2


def test_split_expenses_diff_bank_transaction_id(db):
    # Grouping of expenses with different bank transaction id
    expenses = data['ccc_expenses_split_diff_bank_transaction_id']
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=1)
    general_settings.corporate_credit_card_expenses_object = 'CREDIT CARD PURCHASE'
    general_settings.save()

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=1)
    expense_group_settings.ccc_export_date_type = 'last_spent_at'
    expense_group_settings.split_expense_grouping = 'SINGLE_LINE_ITEM'
    expense_group_settings.save()

    expense_objects = Expense.create_expense_objects(expenses, 1)
    assert len(expense_objects) == 4

    expense_groups = _group_expenses(expense_objects, ['expense_id', 'fund_source', 'employee_email', 'spent_at', 'bank_transaction_id'], 4)
    assert len(expense_groups) == 4

    expense_group_settings.split_expense_grouping = 'MULTIPLE_LINE_ITEM'
    expense_group_settings.save()

    expense_groups = _group_expenses(expense_objects, ['fund_source', 'employee_email', 'spent_at', 'bank_transaction_id'], 4)
    assert len(expense_groups) == 2


def test_format_date():
    date_string = _format_date('2022-05-13T09:32:06.643941Z')

    assert date_string == parser.parse('2022-05-13T09:32:06.643941Z')


def test_create_expense_object_tax_amount(db):
    workspace_id = 1

    payload = data['expenses_tax_amount']
    expenses = Expense.create_expense_objects(payload, workspace_id)
    for expense in expenses:
        if expense.expense_id == payload[0]['id']:
            assert expense.tax_amount == 0
        elif expense.expense_id == payload[1]['id']:
            assert expense.tax_amount == 10
        elif expense.expense_id == payload[2]['id']:
            assert expense.tax_amount == 0
