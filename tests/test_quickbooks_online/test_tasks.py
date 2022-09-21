import ast
import json
import os
import logging
import pytest
import random
from unittest import mock
from django_q.models import Schedule
from apps.tasks.models import TaskLog
from apps.quickbooks_online.models import Bill, BillLineitem, Cheque, QBOExpense, QBOExpenseLineitem, CreditCardPurchase, JournalEntry, \
    JournalEntryLineitem, ChequeLineitem
from apps.quickbooks_online.tasks import create_bill, create_qbo_expense, create_credit_card_purchase, create_journal_entry, get_or_create_credit_card_or_debit_card_vendor, create_cheque, \
    create_bill_payment, check_qbo_object_status, schedule_reimbursements_sync, process_reimbursements, async_sync_accounts, \
        schedule_bill_payment_creation, schedule_qbo_objects_status_sync, get_or_create_credit_card_or_debit_card_vendor, \
            create_or_update_employee_mapping, schedule_bills_creation, update_last_export_details
from fyle_qbo_api.exceptions import BulkError
from qbosdk.exceptions import WrongParamsError
from fyle_accounting_mappings.models import EmployeeMapping, Mapping
from apps.workspaces.models import WorkspaceGeneralSettings, QBOCredential
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping, CategoryMapping, ExpenseAttribute
from apps.mappings.models import GeneralMapping
from apps.fyle.models import ExpenseGroup, Reimbursement, Expense
from apps.quickbooks_online.utils import QBOConnector
from .fixtures import data

logger = logging.getLogger(__name__)


def test_get_or_create_credit_card_or_debit_card_vendor(mocker, db):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor',
        return_value=[]
    )
    workspace_id = 1

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    contact = get_or_create_credit_card_or_debit_card_vendor(workspace_id, 'samp_merchant', True, general_settings)

    assert contact != None

    try:
        with mock.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor') as mock_call:
            mock_call.side_effect = WrongParamsError(msg='wrong parameters', response='wrong parameters')
            contact = get_or_create_credit_card_or_debit_card_vendor(workspace_id, 'samp_merchant', False, general_settings)
    except:
        logger.info('wrong parameters')


def test_create_or_update_employee_mapping(mocker, db):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor',
        return_value=DestinationAttribute.objects.get(value='Vikas')
    )
    workspace_id = 3

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    expense_group = ExpenseGroup.objects.get(id=14)
    expense_group.description.update({'employee_email': 'user4@fyleforgotham.in'})
    expense_group.save()

    source = ExpenseAttribute.objects.filter(
            attribute_type='EMPLOYEE', value__iexact='user4@fyleforgotham.in', workspace_id=workspace_id
        ).first()
    if source:
        employee_mapping = EmployeeMapping.objects.get(source_employee__value='user4@fyleforgotham.in')
        employee_mapping.delete()
    
    create_or_update_employee_mapping(expense_group=expense_group, qbo_connection=qbo_connection, auto_map_employees_preference='EMAIL')

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor') as mock_call:
        employee_mapping = EmployeeMapping.objects.get(source_employee__value='user4@fyleforgotham.in')
        employee_mapping.delete()

        mock_call.side_effect = WrongParamsError(
            msg={
                'Message': 'Invalid parametrs'
            }, response=json.dumps({
                'Fault': {
                    'Error': [{'code': '6240', 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}],
                    'type': 'Invalid_params'
                }
            }))
        try:
            create_or_update_employee_mapping(expense_group=expense_group, qbo_connection=qbo_connection, auto_map_employees_preference='NAME')
        except:
            logger.info('Emplooyee mapping not found')

def test_post_bill_success(mocker, create_task_logs, db):
    mocker.patch(
        'qbosdk.apis.Bills.post',
        return_value=data['post_bill']
    )

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
    
    create_bill(expense_group, task_log.id, False)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    bill = Bill.objects.get(expense_group_id=expense_group.id)
    assert task_log.status=='COMPLETE'
    assert bill.currency == 'USD'
    assert bill.accounts_payable_id == '33'
    assert bill.vendor_id == '31'


def test_create_bill_exceptions(db, create_task_logs):
    workspace_id = 3

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.type = 'CREATING_BILL'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=14)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()

    expense_group.expenses.set(expenses)
    
    with mock.patch('apps.quickbooks_online.models.Bill.create_bill') as mock_call:
        mock_call.side_effect = QBOCredential.DoesNotExist()
        create_bill(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_bill(expense_group, task_log.id, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = Exception()
        create_bill(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        mock_call.side_effect = WrongParamsError(
            msg={
                'Message': 'Invalid parametrs'
            }, response=json.dumps({
                'Fault': {
                    'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}],
                    'type': 'Invalid_params'
                }
            }))
        create_bill(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_post_qbo_expenses_success(mocker, create_task_logs, db):
    mocker.patch(
        'qbosdk.apis.Purchases.post',
        return_value=data['post_purchase']
    )

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

    create_qbo_expense(expense_group, task_log.id, True)

    task_log = TaskLog.objects.get(pk=task_log.id)
    qbo_expense = QBOExpense.objects.get(expense_group_id=expense_group.id)
    assert task_log.status=='COMPLETE'
    assert qbo_expense.currency == 'USD'
    assert qbo_expense.expense_account_id == '35'
    assert qbo_expense.entity_id == '55'


def test_post_qbo_expenses_exceptions(create_task_logs, db):

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

    with mock.patch('apps.quickbooks_online.models.QBOExpense.create_qbo_expense') as mock_call:
        mock_call.side_effect = QBOCredential.DoesNotExist()
        create_qbo_expense(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_qbo_expense(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = Exception()
        create_qbo_expense(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        mock_call.side_effect = WrongParamsError(
            msg={
                'Message': 'Invalid parametrs'
            }, response=json.dumps({
                'Fault': {
                    'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}],
                    'type': 'Invalid_params'
                }
        }))
        create_qbo_expense(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_post_credit_card_purchase_success(mocker, create_task_logs, db):
    mocker.patch(
        'qbosdk.apis.Purchases.post',
        return_value=data['post_purchase']
    )
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor',
        return_value=[]
    )
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
    
    create_credit_card_purchase(expense_group, task_log.id, True)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    credit_card_purchase = CreditCardPurchase.objects.get(expense_group_id=expense_group.id)

    assert task_log.status=='COMPLETE'
    assert credit_card_purchase.currency == 'USD'
    assert credit_card_purchase.ccc_account_id == '41'
    assert credit_card_purchase.entity_id == '58'


def test_post_credit_card_exceptions(mocker, create_task_logs, db):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor',
        return_value=[]
    )
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

    with mock.patch('apps.quickbooks_online.models.CreditCardPurchase.create_credit_card_purchase') as mock_call:
        mock_call.side_effect = QBOCredential.DoesNotExist()
        create_credit_card_purchase(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_credit_card_purchase(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = Exception()
        create_credit_card_purchase(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        mock_call.side_effect = WrongParamsError(
            msg={
                'Message': 'Invalid parametrs'
            }, response=json.dumps({
                'Fault': {
                    'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}],
                    'type': 'Invalid_params'
                }
        }))
        create_credit_card_purchase(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_post_journal_entry_success(mocker, create_task_logs, db):
    mocker.patch(
        'qbosdk.apis.JournalEntries.post',
        return_value=data['post_journal_entry']
    )
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

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.currency = 'GBP'
        expense.save()
    
    expense_group.expenses.set(expenses)
    expense_group.save()
    
    create_journal_entry(expense_group, task_log.id, True)
    
    task_log = TaskLog.objects.get(id=task_log.id)
    journal_entry = JournalEntry.objects.get(expense_group_id=expense_group.id)

    assert task_log.status=='COMPLETE'
    assert journal_entry.currency == 'GBP'
    assert journal_entry.private_note =='Reimbursable expense by ashwin.t@fyle.in on 2022-04-06 '


def test_post_create_journal_entry_exceptions(create_task_logs, db):
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

    with mock.patch('apps.quickbooks_online.models.JournalEntry.create_journal_entry') as mock_call:
        mock_call.side_effect = QBOCredential.DoesNotExist()
        create_journal_entry(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_journal_entry(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = Exception()
        create_journal_entry(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        mock_call.side_effect = WrongParamsError(
            msg={
                'Message': 'Invalid parametrs'
            }, response=json.dumps({
                'Fault': {
                    'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}],
                    'type': 'Invalid_params'
                }
        }))
        create_journal_entry(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_post_cheque_success(mocker, create_task_logs, db):
    mocker.patch(
        'qbosdk.apis.Purchases.post',
        return_value=data['post_purchase']
    )
    mocker.patch(
        'apps.quickbooks_online.tasks.load_attachments',
        return_value=None
    )
    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=14)
    create_cheque(expense_group, task_log.id, True)
    
    task_log = TaskLog.objects.get(id=task_log.id)
    cheque = Cheque.objects.get(expense_group_id=expense_group.id)

    assert task_log.status=='COMPLETE'
    assert cheque.currency == 'USD'
    assert cheque.entity_id == '55'
    assert cheque.private_note =='Reimbursable expense by user9@fyleforgotham.in on 2020-05-13 '


def test_post_create_cheque_exceptions(create_task_logs, db):
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

    with mock.patch('apps.quickbooks_online.models.Cheque.create_cheque') as mock_call:
        mock_call.side_effect = QBOCredential.DoesNotExist()
        create_cheque(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_cheque(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = Exception()
        create_cheque(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        mock_call.side_effect = WrongParamsError(
            msg={
                'Message': 'Invalid parametrs'
            }, response=json.dumps({
                'Fault': {
                    'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}],
                    'type': 'Invalid_params'
                }
        }))
        create_cheque(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_create_bill_payment(mocker, db):
    mocker.patch(
        'apps.quickbooks_online.tasks.load_attachments',
        return_value=[]
    )
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Reimbursements.sync',
        return_value=None
    )
    mocker.patch(
        'qbosdk.apis.Bills.post',
        return_value=data['post_bill']
    )
    mocker.patch(
        'qbosdk.apis.BillPayments.post',
        return_value=data['post_bill']
    )
    mocker.patch(
        'qbosdk.apis.Attachments.post',
        return_value=None
    )
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
    expense_group.save()
    
    create_bill(expense_group, task_log.id, False)

    bill = Bill.objects.last()
    task_log = TaskLog.objects.get(id=task_log.id)
    task_log.expense_group=bill.expense_group
    task_log.save()

    reimbursements = data['reimbursements']

    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=workspace_id)
    create_bill_payment(workspace_id)

    assert task_log.status == 'COMPLETE'


def test_post_bill_payment_exceptions(mocker, db):
    mocker.patch(
        'apps.quickbooks_online.tasks.load_attachments',
        return_value=[]
    )
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Reimbursements.sync',
        return_value=None
    )
    mocker.patch(
        'qbosdk.apis.Bills.post',
        return_value=data['post_bill']
    )
    mocker.patch(
        'qbosdk.apis.BillPayments.post',
        return_value=data['post_bill']
    )
    mocker.patch(
        'qbosdk.apis.Attachments.post',
        return_value=None
    )
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
    expense_group.save()
    
    create_bill(expense_group, task_log.id, False)

    bill = Bill.objects.last()
    task_log = TaskLog.objects.get(id=task_log.id)
    task_log.expense_group=bill.expense_group
    task_log.save()

    reimbursements = data['reimbursements']
    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=workspace_id)
    
    with mock.patch('apps.quickbooks_online.models.BillPayment.create_bill_payment') as mock_call:
        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_bill_payment(workspace_id)

        mock_call.side_effect = Exception()
        create_bill_payment(workspace_id)

        mock_call.side_effect = WrongParamsError(
            msg={
                'Message': 'Invalid parametrs'
            }, response=json.dumps({
                'Fault': {
                    'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}],
                    'type': 'Invalid_params'
                }
        }))
        create_bill_payment(workspace_id)

        try:
            mock_call.side_effect = QBOCredential.DoesNotExist()
            create_bill_payment(workspace_id)
        except:
            logger.info('QBO credentials not found')


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
    
    create_bill(expense_group, task_log.id, False)
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
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Reimbursements.sync',
        return_value=None
    )

    reimbursement_count = Reimbursement.objects.filter(workspace_id=3).count()
    assert reimbursement_count == 0

    process_reimbursements(3)

    reimbursement = Reimbursement.objects.filter(workspace_id=3).count()

    assert reimbursement == 0


def test_async_sync_accounts(mocker, db):
    mocker.patch(
        'apps.quickbooks_online.utils.QBOConnector.sync_accounts',
        return_value=None
    )
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


# def test_schedule_bills_creation(db):

#     schedule_bills_creation(sync_qbo_to_fyle_payments=True, workspace_id=3)

#     schedule_count = Schedule.objects.filter(func='apps.quickbooks_online.tasks.create_bill', args=3).count()
#     assert schedule_count == 1

#     schedule_bills_creation(sync_qbo_to_fyle_payments=False, workspace_id=3)

#     schedule_count = Schedule.objects.filter(func='apps.quickbooks_online.tasks.create_bill', args=3).count()
#     assert schedule_count == 0

def test_update_last_export_details(db):
    workspace_id = 3
    last_export_detail = update_last_export_details(workspace_id)
    assert last_export_detail.export_mode == 'MANUAL'
