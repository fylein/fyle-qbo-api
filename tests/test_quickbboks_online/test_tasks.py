import pytest
import random
from apps.tasks.models import TaskLog
from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.models import Bill, Cheque, QBOExpense, CreditCardPurchase, JournalEntry
from apps.quickbooks_online.tasks import create_bill, create_qbo_expense, create_credit_card_purchase, create_journal_entry, get_or_create_credit_card_or_debit_card_vendor, create_cheque 
from fyle_accounting_mappings.models import EmployeeMapping, Mapping

@pytest.mark.django_db()
def test_post_bill_success(create_task_logs, add_qbo_credentials, add_fyle_credentials):

    task_log = TaskLog.objects.filter(workspace_id=9).first()

    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    
    create_bill(expense_group, task_log.id)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    bill = Bill.objects.get(expense_group_id=expense_group.id)
    assert task_log.status=='COMPLETE'
    assert bill.currency == 'USD'
    assert bill.accounts_payable_id == '33'
    assert bill.vendor_id == '43'

@pytest.mark.django_db()
def test_post_qbo_expenses_success(create_task_logs, add_qbo_credentials, add_fyle_credentials):

    task_log = TaskLog.objects.filter(workspace_id=8).first()

    expense_group = ExpenseGroup.objects.get(id=14)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    
    create_qbo_expense(expense_group, task_log.id)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    qbo_expense = QBOExpense.objects.get(expense_group_id=expense_group.id)
    assert task_log.status=='COMPLETE'
    assert qbo_expense.currency == 'USD'
    assert qbo_expense.expense_account_id == '41'
    assert qbo_expense.entity_id == '55'

@pytest.mark.django_db()
def test_post_credit_card_purchase_success(create_task_logs, add_qbo_credentials, add_fyle_credentials):

    task_log = TaskLog.objects.filter(workspace_id=9).first()

    expense_group = ExpenseGroup.objects.get(id=9)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    
    create_credit_card_purchase(expense_group, task_log.id)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    credit_card_purchase = CreditCardPurchase.objects.get(expense_group_id=expense_group.id)
    assert task_log.status=='COMPLETE'
    assert credit_card_purchase.currency == 'USD'
    assert credit_card_purchase.ccc_account_id == '42'
    assert credit_card_purchase.entity_id == '58'

@pytest.mark.django_db()
def test_post_journal_entry_success(create_task_logs, add_qbo_credentials, add_fyle_credentials):

    task_log = TaskLog.objects.filter(workspace_id=8).first()

    expense_group = ExpenseGroup.objects.get(id=12)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    
    create_journal_entry(expense_group, task_log.id)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    journal_entry = JournalEntry.objects.get(expense_group_id=expense_group.id)
    assert task_log.status=='COMPLETE'
    assert journal_entry.currency == 'USD'
    assert journal_entry.private_note =='Credit card expense by ashwin.t@fyle.in on 2022-01-23 '

@pytest.mark.django_db()
def test_post_journal_entry_success(create_task_logs, add_qbo_credentials, add_fyle_credentials):

    task_log = TaskLog.objects.filter(workspace_id=8).first()

    expense_group = ExpenseGroup.objects.get(id=12)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    
    create_journal_entry(expense_group, task_log.id)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    journal_entry = JournalEntry.objects.get(expense_group_id=expense_group.id)
    assert task_log.status=='COMPLETE'
    assert journal_entry.currency == 'USD'
    assert journal_entry.private_note =='Credit card expense by ashwin.t@fyle.in on 2022-01-23 '

@pytest.mark.django_db()
def test_post_cheque_success(create_task_logs, add_qbo_credentials, add_fyle_credentials):

    task_log = TaskLog.objects.filter(workspace_id=8).first()

    expense_group = ExpenseGroup.objects.get(id=12)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    
    create_cheque(expense_group, task_log.id)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    cheque = Cheque.objects.get(expense_group_id=expense_group.id)
    assert task_log.status=='COMPLETE'
    assert cheque.currency == 'USD'
    assert cheque.entity_id == '55'
    assert cheque.private_note =='Credit card expense by ashwin.t@fyle.in on 2022-01-23 '

@pytest.mark.django_db()
def test_get_or_create_credit_card_or_debit_card_vendor(add_qbo_credentials):
    
    created_vendor = get_or_create_credit_card_or_debit_card_vendor(9,'test Sharma',False)
    
    assert created_vendor.destination_id == '59'
    assert created_vendor.display_name == 'vendor'

@pytest.mark.django_db()
def test_post_bill_mapping_error(create_task_logs, add_qbo_credentials, add_fyle_credentials):

    task_log = TaskLog.objects.filter(workspace_id=9).first()

    EmployeeMapping.objects.filter(workspace_id=9).delete()
    Mapping.objects.filter(
            source_type='CATEGORY',
            destination_type='ACCOUNT',
            workspace_id=9
        ).delete()

    expense_group = ExpenseGroup.objects.get(id=8)
    create_bill(expense_group, task_log.id)

    task_log = TaskLog.objects.filter(pk=task_log.id).first()

    assert task_log.detail[0]['message'] == 'Employee mapping not found'
    assert task_log.detail[1]['message'] == 'Category Mapping not found'
    assert task_log.status == 'FAILED'
