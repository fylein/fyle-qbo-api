import pytest
from datetime import datetime, timezone
from fyle_rest_auth.models import User
from apps.quickbooks_online.utils import Bill,BillLineitem,QBOExpense,QBOExpenseLineitem
from apps.fyle.models import ExpenseGroup
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.quickbooks_online.models import get_department_id_or_none,get_tax_code_id_or_none, get_customer_id_or_none, get_class_id_or_none, get_expense_purpose, get_transaction_date

def test_create_bill(db, add_fyle_credentials):

    expense_group = ExpenseGroup.objects.get(id=8)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=9)
    bill = Bill.create_bill(expense_group)
    bill_lineitems = BillLineitem.create_bill_lineitems(expense_group, workspace_general_settings)

    for bill_lineitem in bill_lineitems:
        assert bill_lineitem.amount == 60.0
        assert bill_lineitem.description == 'ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/8 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txlPjmNxssq1?org_id=orGcBCVPijjO'
        assert bill_lineitem.billable == None

    assert bill.currency == 'USD'
    assert bill.transaction_date == datetime.now().strftime('%Y-%m-%d')
    assert bill.vendor_id == '43'


def test_qbo_expense(db, add_fyle_credentials):

    expense_group = ExpenseGroup.objects.get(id=14)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=8)
    qbo_expense = QBOExpense.create_qbo_expense(expense_group)
    qbo_expense_lineitems  = QBOExpenseLineitem.create_qbo_expense_lineitems(expense_group, workspace_general_settings)

    for qbo_expense_lineitem in qbo_expense_lineitems:
        assert qbo_expense_lineitem.amount == 60.0
        assert qbo_expense_lineitem.description == 'ashwin.t@fyle.in - Food - 2022-01-23 - C/2022/01/R/16 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txRJYVMgMaH6?org_id=or79Cob97KSh'
        assert qbo_expense_lineitem.billable == None

    assert qbo_expense.currency == 'USD'
    assert qbo_expense.transaction_date == datetime.now().strftime('%Y-%m-%d')
    assert qbo_expense.expense_account_id == '41'
    assert qbo_expense.entity_id == '55'


@pytest.mark.django_db(databases=['default'])
def test_get_department_id_or_none():
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        location_id = get_department_id_or_none(expense_group, lineitem)
        assert location_id == None

@pytest.mark.django_db(databases=['default'])
def test_get_tax_code_id_or_none():
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        location_id = get_tax_code_id_or_none(expense_group, lineitem)
        assert location_id == None

@pytest.mark.django_db(databases=['default'])
def test_get_customer_id_or_none():
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        location_id = get_customer_id_or_none(expense_group, lineitem)
        assert location_id == None

@pytest.mark.django_db(databases=['default'])
def test_get_class_id_or_none():
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        location_id = get_class_id_or_none(expense_group, lineitem)
        assert location_id == None

@pytest.mark.django_db(databases=['default'])
def test_get_expense_purpose(add_fyle_credentials):

    expense_group = ExpenseGroup.objects.get(id=8)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=9)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(
            lineitem.category, lineitem.sub_category)
    
        expense_purpose = get_expense_purpose(9,lineitem,category,workspace_general_settings)

        assert expense_purpose == 'ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/8 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txlPjmNxssq1?org_id=orGcBCVPijjO'

@pytest.mark.django_db(databases=['default'])
def test_get_transaction_date():

    expense_group = ExpenseGroup.objects.get(id=8)
    transaction_date = get_transaction_date(expense_group)

    assert transaction_date >= datetime.now().strftime('%Y-%m-%d')
