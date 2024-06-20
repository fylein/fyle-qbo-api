import json
import logging
import random
from unittest import mock

from django_q.models import Schedule
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping, ExpenseAttribute, Mapping
from qbosdk.exceptions import WrongParamsError

from apps.fyle.models import Expense, ExpenseGroup, Reimbursement
from apps.mappings.queues import schedule_bill_payment_creation
from apps.quickbooks_online.exceptions import handle_quickbooks_error
from apps.quickbooks_online.queue import (
    schedule_bills_creation,
    schedule_cheques_creation,
    schedule_credit_card_purchase_creation,
    schedule_journal_entry_creation,
    schedule_qbo_expense_creation,
    schedule_qbo_objects_status_sync,
    schedule_reimbursements_sync,
)
from apps.quickbooks_online.tasks import (
    Bill,
    BillLineitem,
    Cheque,
    CreditCardPurchase,
    Error,
    GeneralMapping,
    JournalEntry,
    QBOExpense,
    QBOExpenseLineitem,
    __validate_expense_group,
    async_sync_accounts,
    check_qbo_object_status,
    create_bill,
    create_bill_payment,
    create_cheque,
    create_credit_card_purchase,
    create_journal_entry,
    create_or_update_employee_mapping,
    create_qbo_expense,
    get_or_create_credit_card_or_debit_card_vendor,
    process_reimbursements,
    update_last_export_details,
)
from apps.quickbooks_online.utils import QBOConnector
from apps.tasks.models import TaskLog
from apps.workspaces.models import QBOCredential, WorkspaceGeneralSettings
from fyle_qbo_api.exceptions import BulkError
from tests.test_quickbooks_online.fixtures import data

logger = logging.getLogger(__name__)


def test_get_or_create_credit_card_or_debit_card_vendor(mocker, db):
    mocker.patch('qbosdk.apis.Vendors.post', return_value=data['post_vendor_resp'])
    mocker.patch('qbosdk.apis.Vendors.search_vendor_by_display_name', return_value=None)
    workspace_id = 1

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    contact = get_or_create_credit_card_or_debit_card_vendor(workspace_id, 'samp_merchant', False, general_settings)
    assert contact.value == 'samp_merchant'

    try:
        with mock.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor') as mock_call:
            mock_call.side_effect = [None, WrongParamsError(msg='wrong parameters', response='wrong parameters')]
            contact = get_or_create_credit_card_or_debit_card_vendor(workspace_id, 'samp_merchant', False, general_settings)
    except Exception:
        logger.info('wrong parameters')

    general_settings.auto_create_merchants_as_vendors = False
    general_settings.save()

    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR', value='Debit Card Misc').delete()

    contact = get_or_create_credit_card_or_debit_card_vendor(workspace_id, '', True, general_settings)
    assert contact.value == 'samp_merchant'

    mocker.patch('qbosdk.apis.Vendors.search_vendor_by_display_name', return_value=data['vendor_response'][0])

    contact = get_or_create_credit_card_or_debit_card_vendor(workspace_id, 'Books by Bessie', True, general_settings)
    assert contact.value == 'Books by Bessie'

    try:
        with mock.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor') as mock_call:
            mock_call.side_effect = WrongParamsError(msg='wrong parameters', response='wrong parameters')
            contact = get_or_create_credit_card_or_debit_card_vendor(workspace_id, 'samp_merchant', False, general_settings)
    except Exception:
        logger.info('wrong parameters')


def test_create_or_update_employee_mapping(mocker, db):
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor', return_value=DestinationAttribute.objects.get(value='Vikas'))
    workspace_id = 3

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    expense_group = ExpenseGroup.objects.get(id=14)
    expense_group.description.update({'employee_email': 'user4@fyleforgotham.in'})
    expense_group.save()

    source = ExpenseAttribute.objects.filter(attribute_type='EMPLOYEE', value__iexact='user4@fyleforgotham.in', workspace_id=workspace_id).first()
    if source:
        employee_mapping = EmployeeMapping.objects.get(source_employee__value='user4@fyleforgotham.in')
        employee_mapping.delete()

    create_or_update_employee_mapping(expense_group=expense_group, qbo_connection=qbo_connection, auto_map_employees_preference='EMAIL')

    with mock.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor') as mock_call:
        employee_mapping = EmployeeMapping.objects.get(source_employee__value='user4@fyleforgotham.in')
        employee_mapping.delete()

        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': '6240', 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        try:
            create_or_update_employee_mapping(expense_group=expense_group, qbo_connection=qbo_connection, auto_map_employees_preference='NAME')
        except Exception:
            logger.info('Employee mapping not found')


def test_post_bill_success(mocker, create_task_logs, db):
    mocker.patch('qbosdk.apis.Bills.post', return_value=data['post_bill'])

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

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)

    general_settings.auto_map_employees = 'NAME'
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    create_bill(expense_group, task_log.id, False)

    task_log = TaskLog.objects.get(pk=task_log.id)
    bill = Bill.objects.get(expense_group_id=expense_group.id)
    assert task_log.status == 'COMPLETE'
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

        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_bill(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_changing_accounting_period(mocker, db, create_task_logs):
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

    with mock.patch('qbosdk.apis.bills.Bills.post') as mock_call:
        mock_call.side_effect = [
            WrongParamsError(
                msg={'Message': 'Invalid Parameters'},
                response=json.dumps(
                    {
                        'Fault': {
                            'type': 'ValidationFault',
                            'Error': [
                                {
                                    'code': 6210,
                                    'Message': 'Account Period Closed, Cannot Update Through Services API',
                                    'Detail': 'The account period has closed and the account books cannot be updated \
                                        through through the QBO Services API. \
                                            Please use the QBO website to make these changes.',
                                }
                            ],
                        }
                    }
                ),
            ),
            data['post_bill'],
        ]

        workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=task_log.workspace_id)
        workspace_general_settings.change_accounting_period = False
        workspace_general_settings.save()

        create_bill(expense_group, task_log.id, False)
        errors = Error.objects.filter(workspace_id=task_log.workspace_id, is_resolved=False, error_title='ValidationFault / 6210').all()

        task_log = TaskLog.objects.get(id=task_log.id)
        assert errors.count() == 1
        assert task_log.status == 'FAILED'

        mock_call.side_effect = [
            WrongParamsError(
                msg={'Message': 'Invalid Parameters'},
                response=json.dumps(
                    {
                        'Fault': {
                            'type': 'ValidationFault',
                            'Error': [
                                {
                                    'code': 6210,
                                    'Message': 'Account Period Closed, Cannot Update Through Services API',
                                    'Detail': 'The account period has closed and the account books cannot be updated \
                                        through through the QBO Services API. \
                                            Please use the QBO website to make these changes.',
                                }
                            ],
                        }
                    }
                ),
            ),
            data['post_bill'],
        ]

        mocker.patch('qbosdk.apis.Preferences.get', return_value=data['preference_response'])

        errors = Error.objects.filter(workspace_id=task_log.workspace_id, is_resolved=False, error_title='ValidationFault / 6210').all()

        assert errors.count() == 1

        workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=task_log.workspace_id)
        workspace_general_settings.change_accounting_period = True
        workspace_general_settings.save()

        create_bill(expense_group, task_log.id, False)
        errors = Error.objects.filter(workspace_id=task_log.workspace_id, is_resolved=False, error_title='ValidationFault / 6210').all()

        task_log = TaskLog.objects.get(id=task_log.id)
        assert errors.count() == 0
        assert task_log.status == 'COMPLETE'


def test_post_qbo_expenses_success(mocker, create_task_logs, db):
    mocker.patch('qbosdk.apis.Purchases.post', return_value=data['post_purchase'])

    mocker.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor', return_value=[])

    mocker.patch('apps.quickbooks_online.tasks.load_attachments', return_value=None)

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
    qbo_expense_lineitem.expense_id = 24
    qbo_expense_lineitem.save()

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)

    general_settings.auto_map_employees = 'NAME'
    general_settings.auto_create_destination_entity = True
    general_settings.import_tax_codes = True
    general_settings.save()

    general_mapping = GeneralMapping.objects.get(workspace_id=3)

    general_mapping.default_tax_code_id = 'tggu76WXIdjY'
    general_mapping.default_tax_code_name = 'GST-free capital - 0%'
    general_mapping.save()

    create_qbo_expense(expense_group, task_log.id, True)

    task_log = TaskLog.objects.get(pk=task_log.id)
    qbo_expense = QBOExpense.objects.get(expense_group_id=expense_group.id)
    assert task_log.status == 'COMPLETE'
    assert qbo_expense.currency == 'USD'
    assert qbo_expense.expense_account_id == '35'
    assert qbo_expense.entity_id == '55'

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=18)

    create_qbo_expense(expense_group, task_log.id, True)

    task_log = TaskLog.objects.get(pk=task_log.id)
    qbo_expense = QBOExpense.objects.get(expense_group_id=expense_group.id)

    assert task_log.status == 'COMPLETE'
    assert qbo_expense.currency == 'USD'


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
    qbo_expense_lineitem.expense_id = 24
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

        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_qbo_expense(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_post_credit_card_purchase_success(mocker, create_task_logs, db):
    mocker.patch('qbosdk.apis.Purchases.post', return_value=data['post_purchase'])
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor', return_value=[])
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

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)

    general_settings.map_merchant_to_vendor = False
    general_settings.auto_map_employees = 'NAME'
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    create_credit_card_purchase(expense_group, task_log.id, True)

    task_log = TaskLog.objects.get(pk=task_log.id)
    credit_card_purchase = CreditCardPurchase.objects.get(expense_group_id=expense_group.id)

    assert task_log.status == 'COMPLETE'
    assert credit_card_purchase.currency == 'USD'
    assert credit_card_purchase.ccc_account_id == '41'
    assert credit_card_purchase.entity_id == '55'


def test_post_credit_card_exceptions(mocker, create_task_logs, db):
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor', return_value=[])
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

        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_credit_card_purchase(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_post_journal_entry_success(mocker, create_task_logs, db):
    mocker.patch('qbosdk.apis.JournalEntries.post', return_value=data['post_journal_entry'])
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

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)

    general_settings.auto_map_employees = 'NAME'
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    create_journal_entry(expense_group, task_log.id, True)

    task_log = TaskLog.objects.get(id=task_log.id)
    journal_entry = JournalEntry.objects.get(expense_group_id=expense_group.id)

    assert task_log.status == 'COMPLETE'
    assert journal_entry.currency == 'GBP'
    assert journal_entry.private_note == 'Reimbursable expense by ashwin.t@fyle.in on 2022-04-06 '

    expense_group = ExpenseGroup.objects.get(id=51)

    task_log = TaskLog.objects.filter(workspace_id=5).first()
    task_log.status = 'READY'
    task_log.save()

    create_journal_entry(expense_group, task_log.id, True)

    task_log = TaskLog.objects.get(id=task_log.id)
    journal_entry = JournalEntry.objects.get(expense_group_id=expense_group.id)

    assert task_log.status == 'COMPLETE'
    assert journal_entry.currency == 'INR'
    assert journal_entry.private_note == 'Reimbursable expense by ashwin.t@fyle.in on 2022-04-06 '


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

        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_journal_entry(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_post_cheque_success(mocker, create_task_logs, db):
    mocker.patch('qbosdk.apis.Purchases.post', return_value=data['post_purchase'])
    mocker.patch('apps.quickbooks_online.tasks.load_attachments', return_value=None)
    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=14)
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)

    general_settings.auto_map_employees = 'EMPLOYEE_CODE'
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    create_cheque(expense_group, task_log.id, True)

    task_log = TaskLog.objects.get(id=task_log.id)
    cheque = Cheque.objects.get(expense_group_id=expense_group.id)

    assert task_log.status == 'COMPLETE'
    assert cheque.currency == 'USD'
    assert cheque.entity_id == '55'
    assert cheque.private_note == 'Reimbursable expense by user9@fyleforgotham.in on 2020-05-13 '


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

        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_cheque(expense_group, task_log.id, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_create_bill_payment(mocker, db):
    mocker.patch('apps.quickbooks_online.tasks.load_attachments', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.Reimbursements.sync', return_value=None)
    mocker.patch('qbosdk.apis.Bills.post', return_value=data['post_bill'])
    mocker.patch('qbosdk.apis.BillPayments.post', return_value=data['post_bill'])
    mocker.patch('qbosdk.apis.Attachments.post', return_value=None)
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
    task_log.expense_group = bill.expense_group
    task_log.save()

    reimbursements = data['reimbursements']

    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=workspace_id)
    create_bill_payment(workspace_id)

    assert task_log.status == 'COMPLETE'


def test_post_bill_payment_exceptions(mocker, db):
    mocker.patch('apps.quickbooks_online.tasks.load_attachments', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.Reimbursements.sync', return_value=None)
    mocker.patch('qbosdk.apis.Bills.post', return_value=data['post_bill'])
    mocker.patch('qbosdk.apis.BillPayments.post', return_value=data['post_bill'])
    mocker.patch('qbosdk.apis.Attachments.post', return_value=None)
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
    task_log.expense_group = bill.expense_group
    task_log.save()

    reimbursements = data['reimbursements']
    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=workspace_id)

    with mock.patch('apps.quickbooks_online.models.BillPayment.create_bill_payment') as mock_call:
        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_bill_payment(workspace_id)

        mock_call.side_effect = Exception()
        create_bill_payment(workspace_id)

        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_bill_payment(workspace_id)

        try:
            mock_call.side_effect = QBOCredential.DoesNotExist()
            create_bill_payment(workspace_id)
        except Exception:
            logger.info('QBO credentials not found')


def test_schedule_bill_payment_creation(db):

    schedule_bill_payment_creation(sync_fyle_to_qbo_payments=True, workspace_id=3)
    schedule = Schedule.objects.filter(func='apps.quickbooks_online.tasks.create_bill_payment').count()

    assert schedule == 1

    schedule_bill_payment_creation(sync_fyle_to_qbo_payments=False, workspace_id=3)
    schedule = Schedule.objects.filter(func='apps.quickbooks_online.tasks.create_bill_payment').count()

    assert schedule == 0


def test_handle_quickbooks_errors(db):
    expense_group = ExpenseGroup.objects.get(id=8)
    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()

    handle_quickbooks_error(exception=WrongParamsError(msg='Some Parameters are wrong', response=json.dumps({'error': 'invalid_grant'})), expense_group=expense_group, task_log=task_log, export_type='Bill')

    qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

    assert qbo_credentials.refresh_token == None
    assert qbo_credentials.is_expired == True
    assert task_log.quickbooks_errors['error'] == 'invalid_grant'

    handle_quickbooks_error(exception=WrongParamsError(msg='Some Parameters are wrong', response=json.dumps({'blewblew': 'invalid_grant'})), expense_group=expense_group, task_log=task_log, export_type='Bill')

    assert 'error' not in task_log.quickbooks_errors

    handle_quickbooks_error(
        exception=WrongParamsError(
            msg='Some Parameters are wrong',
            response=json.dumps(
                {
                    'Fault': {
                        'type': 'ValidationFault',
                        'Error': [
                            {
                                'code': 6210,
                                'Message': 'Account Period Closed, Cannot Update Through Services API',
                                'Detail': 'The account period has closed and the account books cannot be updated \
                                    through through the QBO Services API. \
                                        Please use the QBO website to make these changes.',
                            }
                        ],
                    }
                }
            ),
        ),
        expense_group=expense_group,
        task_log=task_log,
        export_type='Bill Payment',
    )

    errors = Error.objects.filter(workspace_id=task_log.workspace_id, is_resolved=False, error_title='ValidationFault / 6210').all()

    assert errors.count() == 0


def test_check_qbo_object_status(mocker, db):
    mocker.patch('qbosdk.apis.Bills.get_by_id', return_value=data['bill_response'])

    expense_group = ExpenseGroup.objects.get(id=8)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    bill = Bill.create_bill(expense_group)
    BillLineitem.create_bill_lineitems(expense_group, workspace_general_settings)

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    task_log.expense_group = bill.expense_group
    task_log.detail = data['post_bill']
    task_log.bill = bill
    task_log.quickbooks_errors = None
    task_log.status = 'COMPLETE'
    task_log.save()

    check_qbo_object_status(3)
    bills = Bill.objects.filter(expense_group__workspace_id=3)

    for bill in bills:
        assert bill.paid_on_qbo == True
        assert bill.payment_synced == True


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

    mocker.patch('fyle_integrations_platform_connector.apis.Reports.bulk_mark_as_paid', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.Reimbursements.sync', return_value=[])
    workspace_id = 3

    reimbursements = data['reimbursements']

    expenses = Expense.objects.filter(fund_source='PERSONAL')
    for expense in expenses:
        expense.paid_on_qbo = True
        expense.save()

    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=workspace_id)

    reimbursement = Reimbursement.objects.filter(workspace_id=workspace_id).first()
    reimbursement.state = 'PENDING'
    reimbursement.save()

    process_reimbursements(workspace_id)

    reimbursement = Reimbursement.objects.filter(workspace_id=workspace_id).count()

    assert reimbursement == 1


def test_async_sync_accounts(mocker, db):
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.sync_accounts', return_value=None)
    old_accounts = DestinationAttribute.objects.filter(attribute_type='ACCOUNT', workspace_id=3).count()
    assert old_accounts == 63

    async_sync_accounts(3)
    new_accounts = DestinationAttribute.objects.filter(attribute_type='ACCOUNT', workspace_id=3).count()
    assert new_accounts == 63


def test_schedule_qbo_objects_status_sync(db):
    schedule_qbo_objects_status_sync(sync_qbo_to_fyle_payments=True, workspace_id=3)

    schedule_count = Schedule.objects.filter(func='apps.quickbooks_online.tasks.check_qbo_object_status', args=3).count()
    assert schedule_count == 1

    schedule_qbo_objects_status_sync(sync_qbo_to_fyle_payments=False, workspace_id=3)

    schedule_count = Schedule.objects.filter(func='apps.quickbooks_online.tasks.check_qbo_object_status', args=3).count()
    assert schedule_count == 0


def test_update_last_export_details(db):
    workspace_id = 3
    last_export_detail = update_last_export_details(workspace_id)
    assert last_export_detail.export_mode == 'MANUAL'


def test__validate_expense_group(mocker, db):
    workspace_id = 3

    expense_group = ExpenseGroup.objects.get(id=17)

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    general_settings.corporate_credit_card_expenses_object = 'BILL'
    general_settings.reimbursable_expenses_object = 'CHECK'
    general_settings.import_tax_codes = True
    general_settings.save()

    general_mapping = GeneralMapping.objects.filter(workspace_id=workspace_id)
    general_mapping.update(**data['empty_general_maapings'])

    try:
        __validate_expense_group(expense_group, general_settings)
    except BulkError as exception:
        logger.info(exception.response)

    general_settings.reimbursable_expenses_object = 'EXPENSE'
    general_settings.save()

    try:
        __validate_expense_group(expense_group, general_settings)
    except Exception:
        logger.info('Mappings are missing')

    expense_group.description.update({'employee_email': 'ashwin.t@fyle.in'})
    expense_group.save()

    general_settings.corporate_credit_card_expenses_object = 'CREDIT CARD PURCHASE'
    general_settings.save()

    try:
        __validate_expense_group(expense_group, general_settings)
    except Exception:
        logger.info('Mappings are missing')

    general_settings.corporate_credit_card_expenses_object = 'DEBIT CARD EXPENSE'
    general_settings.map_merchant_to_vendor = False
    general_settings.employee_field_mapping = 'VENDOR'
    general_settings.save()

    entity = EmployeeMapping.objects.get(source_employee__value=expense_group.description.get('employee_email'), workspace_id=expense_group.workspace_id)
    entity.destination_vendor = None
    entity.save()

    try:
        __validate_expense_group(expense_group, general_settings)
    except Exception:
        logger.info('Mappings are missing')

    Mapping.objects.filter(source_type='CATEGORY', destination_type='ACCOUNT', source__value='Food', workspace_id=expense_group.workspace_id).delete()

    try:
        __validate_expense_group(expense_group, general_settings)
    except Exception:
        logger.info('Mappings are missing')

    general_mapping = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
    general_mapping.delete()
    try:
        __validate_expense_group(expense_group, general_settings)
    except Exception:
        logger.info('Mappings are missing')


def test_schedule_credit_card_purchase_creation(db):
    workspace_id = 3

    expense_group = ExpenseGroup.objects.get(id=17)
    expense_group.exported_at = None
    expense_group.save()

    credit_card_purchase = CreditCardPurchase.objects.filter(expense_group__id=expense_group.id).first()
    credit_card_purchase.expense_group = ExpenseGroup.objects.get(id=19)
    credit_card_purchase.save()

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    task_log.status = 'READY'
    task_log.save()

    schedule_credit_card_purchase_creation(workspace_id, [17], False, 'CCC')

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    assert task_log.type == 'CREATING_CREDIT_CARD_PURCHASE'


def test_schedule_bills_creation(db):
    workspace_id = 4

    expense_group = ExpenseGroup.objects.get(id=23)
    expense_group.exported_at = None
    expense_group.save()

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    task_log.status = 'READY'
    task_log.save()

    schedule_bills_creation(workspace_id, [23], False, 'PERSONAL')

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    assert task_log.type == 'CREATING_BILL'


def test_schedule_cheques_creation(db):
    workspace_id = 4

    expense_group = ExpenseGroup.objects.get(id=23)
    expense_group.exported_at = None
    expense_group.save()

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    task_log.status = 'READY'
    task_log.save()

    schedule_cheques_creation(workspace_id, [23], False, 'PERSONAL')

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    assert task_log.type == 'CREATING_CHECK'


def test_schedule_qbo_expense_creation(db):
    workspace_id = 4

    expense_group = ExpenseGroup.objects.get(id=23)
    expense_group.exported_at = None
    expense_group.save()

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    task_log.status = 'READY'
    task_log.save()

    schedule_qbo_expense_creation(workspace_id, [23], False, 'PERSONAL')

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    assert task_log.type == 'CREATING_EXPENSE'


def test_schedule_journal_entry_creation(db):
    workspace_id = 4

    expense_group = ExpenseGroup.objects.get(id=23)
    expense_group.exported_at = None
    expense_group.save()

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    task_log.status = 'READY'
    task_log.save()

    schedule_journal_entry_creation(workspace_id, [23], False, 'PERSONAL')

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    assert task_log.type == 'CREATING_JOURNAL_ENTRY'
