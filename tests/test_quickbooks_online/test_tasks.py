import ast
import os
import pytest
import logging
import random
from django_q.models import Schedule
from apps.tasks.models import TaskLog
from apps.quickbooks_online.models import Bill, Cheque, QBOExpense, QBOExpenseLineitem, CreditCardPurchase, JournalEntry, \
    JournalEntryLineitem, ChequeLineitem
from apps.quickbooks_online.tasks import create_bill, create_qbo_expense, create_credit_card_purchase, create_journal_entry, get_or_create_credit_card_or_debit_card_vendor, create_cheque, \
    create_bill_payment, check_qbo_object_status, schedule_reimbursements_sync, process_reimbursements, async_sync_accounts, \
        schedule_bill_payment_creation, schedule_qbo_objects_status_sync 
from fyle_accounting_mappings.models import EmployeeMapping, Mapping
from apps.workspaces.models import WorkspaceGeneralSettings, QBOCredential
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping, CategoryMapping, ExpenseAttribute
from apps.mappings.models import GeneralMapping
from apps.fyle.models import ExpenseGroup, Reimbursement, Expense
from apps.quickbooks_online.utils import QBOConnector

logger = logging.getLogger(__name__)


def test_post_bill_success(create_task_logs, db):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=14)
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
    assert bill.vendor_id == '31'
    
    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_credentials.delete()
    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()
    
    create_bill(expense_group, task_log.id)

    final_task_log = TaskLog.objects.get(id=task_log.id)
    assert final_task_log.detail['message'] == 'QBO Account not connected'


def test_post_bill_mapping_errors(create_task_logs, db):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    CategoryMapping.objects.filter(workspace_id=3).delete()
    EmployeeMapping.objects.filter(workspace_id=3).delete()

    expense_group = ExpenseGroup.objects.get(id=8)
    create_bill(expense_group, task_log.id)

    task_log = TaskLog.objects.filter(pk=task_log.id).first()

    assert task_log.detail[0]['message'] == 'Employee mapping not found'
    assert task_log.status == 'FAILED'


def test_bill_accounting_period_working(create_task_logs, db):
    task_log = TaskLog.objects.filter(workspace_id=3).first()

    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)

    spent_at = {'spent_at': '2000-09-14'}
    expense_group.description.update(spent_at)
    workaspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workaspace_general_setting.change_accounting_period = True
    workaspace_general_setting.save()

    create_bill(expense_group, task_log.id)
    
    task_log = TaskLog.objects.get(pk=task_log.id)

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    assert task_log.status == 'COMPLETE'


def test_post_qbo_expenses_success(create_task_logs, db):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=14)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    expense_group.save()

    qbo_expense_lineitem = QBOExpenseLineitem.objects.get(expense_id=7)
    qbo_expense_lineitem.expense_id=24
    qbo_expense_lineitem.save()

    create_qbo_expense(expense_group, task_log.id)

    task_log = TaskLog.objects.get(pk=task_log.id)
    qbo_expense = QBOExpense.objects.get(expense_group_id=expense_group.id)
    assert task_log.status=='COMPLETE'
    assert qbo_expense.currency == 'USD'
    assert qbo_expense.expense_account_id == '35'
    assert qbo_expense.entity_id == '55'

    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_credentials.delete()

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()
    
    create_qbo_expense(expense_group, task_log.id)

    final_task_log = TaskLog.objects.get(id=task_log.id)
    assert final_task_log.detail['message'] == 'QBO Account not connected'


def test_post_qbo_expense_mapping_errors(create_task_logs, db):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    CategoryMapping.objects.filter(workspace_id=3).delete()
    EmployeeMapping.objects.filter(workspace_id=3).delete()

    expense_group = ExpenseGroup.objects.get(id=8)
    create_qbo_expense(expense_group, task_log.id)

    task_log = TaskLog.objects.filter(pk=task_log.id).first()

    assert task_log.detail[0]['message'] == 'Employee mapping not found'
    assert task_log.status == 'FAILED'


def test_post_credit_card_purchase_success(create_task_logs, db):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

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
    assert credit_card_purchase.ccc_account_id == '41'
    assert credit_card_purchase.entity_id == '58'

    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_credentials.delete()

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()
    
    create_credit_card_purchase(expense_group, task_log.id)

    final_task_log = TaskLog.objects.get(id=task_log.id)
    assert final_task_log.detail['message'] == 'QBO Account not connected'


def test_post_create_credit_card_purchase_mapping_errors(create_task_logs, db):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    CategoryMapping.objects.filter(workspace_id=3).delete()
    EmployeeMapping.objects.filter(workspace_id=3).delete()

    expense_group = ExpenseGroup.objects.get(id=8)
    create_credit_card_purchase(expense_group, task_log.id)

    task_log = TaskLog.objects.filter(pk=task_log.id).first()

    assert task_log.detail[0]['message'] == 'Employee mapping not found'
    assert task_log.status == 'FAILED'


def test_post_journal_entry_success(create_task_logs, db):

    task_log = TaskLog.objects.filter(workspace_id=5).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=50)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    expense_group.save()
    
    create_journal_entry(expense_group, task_log.id)

    task_log = TaskLog.objects.get(id=task_log.id)
    assert task_log.status=='FAILED'

    task_log = TaskLog.objects.filter(workspace_id=5).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=53)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.currency = 'GBP'
        expense.save()
    
    expense_group.expenses.set(expenses)
    expense_group.save()
    
    create_journal_entry(expense_group, task_log.id)
    
    task_log = TaskLog.objects.get(id=task_log.id)
    journal_entry = JournalEntry.objects.get(expense_group_id=expense_group.id)

    assert task_log.status=='COMPLETE'
    assert journal_entry.currency == 'GBP'
    assert journal_entry.private_note =='Reimbursable expense by ashwin.t@fyle.in on 2022-05-25 '

    qbo_credentials = QBOCredential.objects.get(workspace_id=5)
    qbo_credentials.delete()

    task_log = TaskLog.objects.filter(workspace_id=5).first()
    task_log.status = 'READY'
    task_log.save()
    
    create_journal_entry(expense_group, task_log.id)
    final_task_log = TaskLog.objects.get(id=task_log.id)

    assert final_task_log.detail['message'] == 'QBO Account not connected'


def test_post_create_journal_entry_mapping_errors(create_task_logs, db):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    CategoryMapping.objects.filter(workspace_id=3).delete()
    EmployeeMapping.objects.filter(workspace_id=3).delete()

    expense_group = ExpenseGroup.objects.get(id=8)
    create_journal_entry(expense_group, task_log.id)

    task_log = TaskLog.objects.filter(pk=task_log.id).first()

    assert task_log.detail[0]['message'] == 'Employee mapping not found'
    assert task_log.status == 'FAILED'


def test_post_cheque_success(create_task_logs, db):

    task_log = TaskLog.objects.filter(workspace_id=5).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=50)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    expense_group.save()
    
    create_cheque(expense_group, task_log.id)

    task_log = TaskLog.objects.get(id=task_log.id)
    assert task_log.status=='FAILED'

    task_log = TaskLog.objects.filter(workspace_id=5).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=53)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.currency = 'GBP'
        expense.save()
    
    expense_group.expenses.set(expenses)
    expense_group.save()
    
    create_cheque(expense_group, task_log.id)
    
    task_log = TaskLog.objects.get(id=task_log.id)
    cheque = Cheque.objects.get(expense_group_id=expense_group.id)

    assert task_log.status=='COMPLETE'
    assert cheque.currency == 'GBP'
    assert cheque.entity_id == '84'
    assert cheque.private_note =='Reimbursable expense by ashwin.t@fyle.in on 2022-05-25 '

    qbo_credentials = QBOCredential.objects.get(workspace_id=5)
    qbo_credentials.delete()

    task_log = TaskLog.objects.filter(workspace_id=5).first()
    task_log.status = 'READY'
    task_log.save()
    
    create_cheque(expense_group, task_log.id)

    final_task_log = TaskLog.objects.get(id=task_log.id)
    assert final_task_log.detail['message'] == 'QBO Account not connected'


def test_post_create_cheque_mapping_errors(create_task_logs, db):

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    CategoryMapping.objects.filter(workspace_id=3).delete()
    EmployeeMapping.objects.filter(workspace_id=3).delete()

    expense_group = ExpenseGroup.objects.get(id=8)
    create_cheque(expense_group, task_log.id)

    task_log = TaskLog.objects.filter(pk=task_log.id).first()

    assert task_log.detail[0]['message'] == 'Employee mapping not found'
    assert task_log.status == 'FAILED'

def test_get_or_create_credit_card_or_debit_card_vendor(db):
    
    created_vendor = get_or_create_credit_card_or_debit_card_vendor(3,'test Sharma',False)
    
    assert created_vendor.destination_id == '59'
    assert created_vendor.display_name == 'vendor'


def test_create_bill_payment(db):
    workspace_id = 3
    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=14)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    
    create_bill(expense_group, task_log.id)

    bill = Bill.objects.last()
    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.expense_group=bill.expense_group
    task_log.save()

    create_bill_payment(workspace_id)

    assert task_log.status == 'COMPLETE'

    bill = Bill.objects.last()
    bill.payment_synced = False
    bill.save()

    qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
    qbo_credentials.delete()

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.save()
    try:
        create_bill_payment(workspace_id)
    except:
        logger.info('QBO Account not connected')


def test_schedule_bill_payment_creation(db):

    schedule_bill_payment_creation(sync_fyle_to_qbo_payments=True, workspace_id=3)
    schedule = Schedule.objects.filter(func='apps.quickbooks_online.tasks.create_bill_payment').count()

    assert schedule == 1

    schedule_bill_payment_creation(sync_fyle_to_qbo_payments=False, workspace_id=3)
    schedule = Schedule.objects.filter(func='apps.quickbooks_online.tasks.create_bill_payment').count()

    assert schedule == 0


def test_check_qbo_object_status(db):
    
    expense_group = ExpenseGroup.objects.get(id=14)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)
    expense_group.save()

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.expense_group = expense_group
    task_log.save()
    
    create_bill(expense_group, task_log.id)
    task_log = TaskLog.objects.get(id=task_log.id)
    
    check_qbo_object_status(3)
    bills = Bill.objects.filter(expense_group__workspace_id=3)

    for bill in bills: 
        assert bill.paid_on_qbo == False
        assert bill.payment_synced == False


def test_schedule_reimbursements_sync(db):

    schedule = Schedule.objects.filter(func='apps.quickbooks_online.tasks.process_reimbursements', args=3).count()
    assert schedule == 0

    schedule_reimbursements_sync(sync_qbo_to_fyle_payments=True, workspace_id=3)

    schedule_count = Schedule.objects.filter(func='apps.quickbooks_online.tasks.process_reimbursements', args=3).count()
    assert schedule_count == 1

    schedule_reimbursements_sync(sync_qbo_to_fyle_payments=False, workspace_id=3)

    schedule_count = Schedule.objects.filter(func='apps.quickbooks_online.tasks.process_reimbursements', args=3).count()
    assert schedule_count == 0


def test_process_reimbursements(db, mocker):

    mocker.patch(
        'fyle_integrations_platform_connector.apis.Reimbursements.bulk_post_reimbursements',
        return_value=[]
    )

    reimbursement_count = Reimbursement.objects.filter(workspace_id=3).count()
    assert reimbursement_count == 0

    process_reimbursements(3)

    reimbursement = Reimbursement.objects.filter(workspace_id=3).count()

    assert reimbursement == 213


def test_async_sync_accounts(db):
    old_accounts = DestinationAttribute.objects.filter(
        attribute_type='ACCOUNT', workspace_id=3).count()
    assert old_accounts == 63
    
    async_sync_accounts(3)
    new_accounts = DestinationAttribute.objects.filter(
        attribute_type='ACCOUNT', workspace_id=3).count()
    assert new_accounts == 63


def test_schedule_qbo_objects_status_sync(db):
    schedule_qbo_objects_status_sync(sync_qbo_to_fyle_payments=True, workspace_id=3)

    schedule_count = Schedule.objects.filter(func='apps.quickbooks_online.tasks.check_qbo_object_status', args=3).count()
    assert schedule_count == 1

    schedule_qbo_objects_status_sync(sync_qbo_to_fyle_payments=False, workspace_id=3)

    schedule_count = Schedule.objects.filter(func='apps.quickbooks_online.tasks.check_qbo_object_status', args=3).count()
    assert schedule_count == 0
