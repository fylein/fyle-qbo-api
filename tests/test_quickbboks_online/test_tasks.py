import pytest
import random
from apps.tasks.models import TaskLog
from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.models import Bill, Cheque, QBOExpense, CreditCardPurchase, JournalEntry
from apps.quickbooks_online.tasks import create_bill, create_qbo_expense, create_credit_card_purchase, create_journal_entry, get_or_create_credit_card_or_debit_card_vendor, create_cheque 
from fyle_accounting_mappings.models import EmployeeMapping, Mapping
from apps.workspaces.models import WorkspaceGeneralSettings, QBOCredential
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping, CategoryMapping, ExpenseAttribute
from apps.mappings.models import GeneralMapping


@pytest.mark.django_db()
def test_post_bill_success(create_task_logs):

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

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    workaspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workaspace_general_setting.auto_map_employees = 'NAME'
    workaspace_general_setting.auto_create_destination_entity = True
    workaspace_general_setting.save()

    expense_group = ExpenseGroup.objects.filter(workspace_id=3).first()

    source_employee = ExpenseAttribute.objects.get(
        workspace_id=expense_group.workspace_id,
        attribute_type='EMPLOYEE',
        value=expense_group.description.get('employee_email')
    )
    source_employee.value = 'new_employeeee@fyle.in'
    source_employee.detail.update({'full_name': 'Fyle new employeeee'})
    source_employee.save()

    expense_group.description.update({'employee_email': 'new_employeeee@fyle.in'})
    expense_group.save()

    expenses = expense_group.expenses.all()

    general_mapping = GeneralMapping.objects.get(workspace_id=3)
    general_mapping.location_name = "01: San Francisco"
    general_mapping.location_id = 2
    general_mapping.save()
    
    for expense in expenses:
        expense.employee_email = 'new_employeeee@fyle.in'
        expense.save()
    
    expense_group.expenses.set(expenses)

    mapping = EmployeeMapping.objects.get(
        source_employee__value=expense_group.description.get('employee_email'),
        workspace_id=expense_group.workspace_id
    )
    mapping.delete()

    create_bill(expense_group, task_log.id)

    task_log = TaskLog.objects.filter(pk=task_log.id).first()
    print(task_log.detail)
    assert task_log.detail[0]['message'] == 'Employee mapping not found'

    qbo_credentials = QBOCredential.objects.get(workspace_id=3)
    qbo_credentials.delete()
    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()
    
    create_bill(expense_group, task_log.id)

    final_task_log = TaskLog.objects.get(id=task_log.id)
    print(final_task_log.detail)
    final_task_log.detail['message'] == 'QBO Account not connected'

@pytest.mark.django_db()
def test_post_bill_mapping_errors(create_task_logs):

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


@pytest.mark.django_db()
def test_accounting_period_working(create_task_logs):
    task_log = TaskLog.objects.filter(workspace_id=3).first()

    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
    
    expense_group.expenses.set(expenses)

    spent_at = {'spent_at': '2012-09-14'}
    expense_group.description.update(spent_at)
    workaspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workaspace_general_setting.change_accounting_period = False
    workaspace_general_setting.save()

    create_bill(expense_group, task_log.id)
    
    task_log = TaskLog.objects.get(pk=task_log.id)

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    print(task_log.detail)
    assert task_log.status == 'COMPLETE'

    workaspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workaspace_general_setting.change_accounting_period = True
    workaspace_general_setting.save()

    create_bill(expense_group, task_log.id)
    bill = Bill.objects.get(expense_group_id=expense_group.id)
    task_log = TaskLog.objects.get(pk=task_log.id)

    assert task_log.status=='COMPLETE'
    assert bill.entity_id=='1674'
    assert bill.currency=='1'
    assert bill.location_id=='8'
    assert bill.accounts_payable_id=='25'

@pytest.mark.django_db()
def test_post_qbo_expenses_success(create_task_logs):

    task_log = TaskLog.objects.filter(workspace_id=3).first()

    expense_group = ExpenseGroup.objects.get(id=9)
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
def test_post_credit_card_purchase_success(create_task_logs):

    task_log = TaskLog.objects.filter(workspace_id=3).first()

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

@pytest.mark.django_db()
def test_post_journal_entry_success(create_task_logs):

    task_log = TaskLog.objects.filter(workspace_id=3).first()

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
def test_post_journal_entry_success(create_task_logs):

    task_log = TaskLog.objects.filter(workspace_id=3).first()

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
def test_post_cheque_success(create_task_logs):

    task_log = TaskLog.objects.filter(workspace_id=3).first()

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
def test_get_or_create_credit_card_or_debit_card_vendor():
    
    created_vendor = get_or_create_credit_card_or_debit_card_vendor(3,'test Sharma',False)
    
    assert created_vendor.destination_id == '59'
    assert created_vendor.display_name == 'vendor'

@pytest.mark.django_db()
def test_post_bill_mapping_error(create_task_logs):

    task_log = TaskLog.objects.filter(workspace_id=3).first()

    EmployeeMapping.objects.filter(workspace_id=3).delete()
    Mapping.objects.filter(
            source_type='CATEGORY',
            destination_type='ACCOUNT',
            workspace_id=3
        ).delete()

    expense_group = ExpenseGroup.objects.get(id=8)
    create_bill(expense_group, task_log.id)

    task_log = TaskLog.objects.filter(pk=task_log.id).first()

    assert task_log.detail[0]['message'] == 'Employee mapping not found'
    assert task_log.detail[1]['message'] == 'Category Mapping not found'
    assert task_log.status == 'FAILED'
