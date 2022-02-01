import pytest
from apps.fyle.models import Expense, ExpenseGroup
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.quickbooks_online.models import Bill,BillLineitem,CreditCardPurchase,CreditCardPurchaseLineitem, JournalEntry, JournalEntryLineitem, QBOExpense, QBOExpenseLineitem,Cheque, ChequeLineitem
from apps.tasks.models import TaskLog
@pytest.fixture
def create_bill(db, add_qbo_credentials, add_fyle_credentials):

    expense_group = ExpenseGroup.objects.get(id=8)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=9)
    bill = Bill.create_bill(expense_group)
    bill_lineitems = BillLineitem.create_bill_lineitems(expense_group, workspace_general_settings)

    return bill, bill_lineitems

@pytest.fixture
def create_credit_card_purchase(db, add_qbo_credentials, add_fyle_credentials):

    expense_group = ExpenseGroup.objects.get(id=9)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=9)
    credit_card_purchase = CreditCardPurchase.create_credit_card_purchase(expense_group, True)
    credit_card_purchase_lineitems  = CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(expense_group, workspace_general_settings)

    return credit_card_purchase,credit_card_purchase_lineitems

@pytest.fixture
def create_journal_entry(db, add_qbo_credentials, add_fyle_credentials):

    expense_group = ExpenseGroup.objects.get(id=12)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=8)
    journal_entry = JournalEntry.create_journal_entry(expense_group)
    journal_entry_lineitems = JournalEntryLineitem.create_journal_entry_lineitems(expense_group,workspace_general_settings)

    return journal_entry,journal_entry_lineitems

@pytest.fixture
def create_qbo_expense(db, add_qbo_credentials, add_fyle_credentials):

    expense_group = ExpenseGroup.objects.get(id=14)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=8)
    qbo_expense = QBOExpense.create_qbo_expense(expense_group)
    qbo_expense_lineitems  = QBOExpenseLineitem.create_qbo_expense_lineitems(expense_group, workspace_general_settings)

    return qbo_expense,qbo_expense_lineitems

@pytest.fixture
def create_cheque(db, add_qbo_credentials, add_fyle_credentials):

    expense_group = ExpenseGroup.objects.get(id=12)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=8)
    cheque = Cheque.create_cheque(expense_group)
    cheque_lineitems  = ChequeLineitem.create_cheque_lineitems(expense_group, workspace_general_settings)

    return cheque,cheque_lineitems

@pytest.fixture
def create_task_logs(db):
    TaskLog.objects.update_or_create(
        workspace_id=8,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'READY'
        }
    )

    TaskLog.objects.update_or_create(
        workspace_id=9,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'READY'
        }
    )
