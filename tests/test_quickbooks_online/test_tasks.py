import json
import logging
import random
from datetime import timedelta
from unittest import mock

import pytest
from django.utils import timezone as django_timezone
from django_q.models import Schedule
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping, ExpenseAttribute, Mapping
from qbosdk.exceptions import WrongParamsError

from apps.fyle.models import Expense, ExpenseGroup, Reimbursement
from apps.mappings.queues import schedule_bill_payment_creation
from apps.quickbooks_online.exceptions import handle_qbo_invalid_token_error, handle_quickbooks_error
from apps.quickbooks_online.queue import (
    handle_skipped_exports,
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
    sync_accounts,
    update_last_export_details,
    validate_for_skipping_payment,
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

    contact, _ = get_or_create_credit_card_or_debit_card_vendor(workspace_id, 'samp_merchant', False, general_settings)
    assert contact.value == 'samp_merchant'

    try:
        with mock.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor') as mock_call:
            mock_call.side_effect = [None, WrongParamsError(msg='wrong parameters', response='wrong parameters')]
            contact, _ = get_or_create_credit_card_or_debit_card_vendor(workspace_id, 'samp_merchant', False, general_settings)
    except Exception:
        logger.info('wrong parameters')

    general_settings.auto_create_merchants_as_vendors = False
    general_settings.save()

    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR', value='Debit Card Misc').delete()

    contact, _ = get_or_create_credit_card_or_debit_card_vendor(workspace_id, '', True, general_settings)
    assert contact.value == 'samp_merchant'

    mocker.patch('qbosdk.apis.Vendors.search_vendor_by_display_name', return_value=data['vendor_response'][0])

    contact, _ = get_or_create_credit_card_or_debit_card_vendor(workspace_id, 'Books by Bessie', True, general_settings)
    assert contact.value == 'Books by Bessie'

    try:
        with mock.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor') as mock_call:
            mock_call.side_effect = WrongParamsError(msg='wrong parameters', response='wrong parameters')
            contact, _ = get_or_create_credit_card_or_debit_card_vendor(workspace_id, 'samp_merchant', False, general_settings)
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

    expense_group = ExpenseGroup.objects.get(id=14)
    expenses = expense_group.expenses.all()
    expense_group.workspace_id = 3
    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.expense_group_id = expense_group.id
    task_log.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.previous_export_state = 'ERROR'
        expense.save()

    expense_group.expenses.set(expenses)

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)

    general_settings.auto_map_employees = 'NAME'
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    create_bill(expense_group.id, task_log.id, False, True)

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
        expense.previous_export_state = 'ERROR'
        expense.save()

    expense_group.expenses.set(expenses)
    qbo_credentials = QBOCredential.objects.filter(workspace_id=expense_group.workspace_id).first()

    with mock.patch('apps.quickbooks_online.models.Bill.create_bill') as mock_call:
        mock_call.side_effect = QBOCredential.DoesNotExist()
        create_bill(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_bill(expense_group.id, task_log.id, True, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = Exception()
        create_bill(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_bill(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_changing_accounting_period(mocker, db, create_task_logs):
    workspace_id = 3

    expense_group = ExpenseGroup.objects.get(id=14)
    expenses = expense_group.expenses.all()
    expense_group.workspace_id = workspace_id
    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.type = 'CREATING_BILL'
    task_log.expense_group_id = expense_group.id
    task_log.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.previous_export_state = 'ERROR'
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

        create_bill(expense_group.id, task_log.id, False, True)
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

        create_bill(expense_group.id, task_log.id, False, True)
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

    DestinationAttribute.objects.create(
        attribute_type="BANK_ACCOUNT",
        display_name="Bank Account",
        value="Cash on hand",
        destination_id="94",
        workspace_id=3,
        active=True,
    )

    expense_group = ExpenseGroup.objects.get(id=14)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.previous_export_state = 'ERROR'
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

    create_qbo_expense(expense_group.id, task_log.id, True, True)

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
    expenses = expense_group.expenses.all()

    for expense in expenses:
        expense.previous_export_state = 'ERROR'
        expense.save()

    create_qbo_expense(expense_group.id, task_log.id, True, True)

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
        expense.previous_export_state = 'ERROR'
        expense.save()

    expense_group.expenses.set(expenses)
    expense_group.save()

    qbo_expense_lineitem = QBOExpenseLineitem.objects.get(expense_id=7)
    qbo_expense_lineitem.expense_id = 24
    qbo_expense_lineitem.save()
    qbo_credentials = QBOCredential.objects.filter(workspace_id=expense_group.workspace_id).first()

    with mock.patch('apps.quickbooks_online.models.QBOExpense.create_qbo_expense') as mock_call:
        mock_call.side_effect = QBOCredential.DoesNotExist()
        create_qbo_expense(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_qbo_expense(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = Exception()
        create_qbo_expense(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_qbo_expense(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_post_credit_card_purchase_success(mocker, create_task_logs, db):
    mocker.patch('qbosdk.apis.Purchases.post', return_value=data['post_purchase'])
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.get_or_create_vendor', return_value=[])

    expense_group = ExpenseGroup.objects.get(id=9)
    expense_group.workspace_id = 3
    expenses = expense_group.expenses.all()
    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.expense_group_id = expense_group.id
    task_log.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.previous_export_state = 'ERROR'
        expense.save()

    expense_group.expenses.set(expenses)

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)

    general_settings.map_merchant_to_vendor = False
    general_settings.auto_map_employees = 'NAME'
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    create_credit_card_purchase(expense_group.id, task_log.id, True, True)

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
        expense.previous_export_state = 'ERROR'
        expense.save()

    expense_group.expenses.set(expenses)
    qbo_credentials = QBOCredential.objects.filter(workspace_id=expense_group.workspace_id).first()

    with mock.patch('apps.quickbooks_online.models.CreditCardPurchase.create_credit_card_purchase') as mock_call:
        mock_call.side_effect = QBOCredential.DoesNotExist()
        create_credit_card_purchase(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_credit_card_purchase(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = Exception()
        create_credit_card_purchase(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_credit_card_purchase(expense_group.id, task_log.id, False, True)

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
        expense.previous_export_state = 'ERROR'
        expense.currency = 'GBP'
        expense.save()

    expense_group.expenses.set(expenses)
    expense_group.save()

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)

    general_settings.auto_map_employees = 'NAME'
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    create_journal_entry(expense_group.id, task_log.id, True, True)

    task_log = TaskLog.objects.get(id=task_log.id)
    journal_entry = JournalEntry.objects.get(expense_group_id=expense_group.id)

    assert task_log.status == 'COMPLETE'
    assert journal_entry.currency == 'GBP'
    assert journal_entry.private_note == 'Reimbursable expense by ashwin.t@fyle.in on 2022-04-06 '

    expense_group = ExpenseGroup.objects.get(id=51)
    expenses = expense_group.expenses.all()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.previous_export_state = 'ERROR'
        expense.save()

    task_log = TaskLog.objects.filter(workspace_id=5).first()
    task_log.status = 'READY'
    task_log.save()

    create_journal_entry(expense_group.id, task_log.id, True, True)

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
        expense.previous_export_state = 'ERROR'
        expense.save()

    expense_group.expenses.set(expenses)
    expense_group.save()

    qbo_credentials = QBOCredential.objects.filter(workspace_id=expense_group.workspace_id).first()

    with mock.patch('apps.quickbooks_online.models.JournalEntry.create_journal_entry') as mock_call:
        mock_call.side_effect = QBOCredential.DoesNotExist()
        create_journal_entry(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_journal_entry(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = Exception()
        create_journal_entry(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_journal_entry(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_post_cheque_success(mocker, create_task_logs, db):
    mocker.patch('qbosdk.apis.Purchases.post', return_value=data['post_purchase'])
    mocker.patch('apps.quickbooks_online.tasks.load_attachments', return_value=None)
    task_log = TaskLog.objects.filter(workspace_id=3).first()
    task_log.status = 'READY'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=14)
    expenses = expense_group.expenses.all()
    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.previous_export_state = 'ERROR'
        expense.save()
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)

    general_settings.auto_map_employees = 'EMPLOYEE_CODE'
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    create_cheque(expense_group.id, task_log.id, True, True)

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
        expense.previous_export_state = 'ERROR'
        expense.save()

    expense_group.expenses.set(expenses)
    expense_group.save()

    qbo_credentials = QBOCredential.objects.filter(workspace_id=expense_group.workspace_id).first()

    with mock.patch('apps.quickbooks_online.models.Cheque.create_cheque') as mock_call:
        mock_call.side_effect = QBOCredential.DoesNotExist()
        create_cheque(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_cheque(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = Exception()
        create_cheque(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        qbo_credentials.is_expired = False
        qbo_credentials.save()
        mock_call.side_effect = WrongParamsError(msg={'Message': 'Invalid parametrs'}, response=json.dumps({'Fault': {'Error': [{'code': 400, 'Message': 'Invalid parametrs', 'Detail': 'Invalid parametrs'}], 'type': 'Invalid_params'}}))
        create_cheque(expense_group.id, task_log.id, False, True)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_create_bill_payment(mocker, db):
    mocker.patch('apps.quickbooks_online.tasks.load_attachments', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.Reimbursements.sync', return_value=None)
    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=[])
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
        expense.previous_export_state = 'ERROR'
        expense.save()

    expense_group.expenses.set(expenses)
    expense_group.save()

    create_bill(expense_group.id, task_log.id, False, True)

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
    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=[])
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
        expense.previous_export_state = 'ERROR'
        expense.save()

    expense_group.expenses.set(expenses)
    expense_group.save()

    create_bill(expense_group.id, task_log.id, False, True)

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


def test_handle_quickbooks_errors(mocker, db):
    expense_group = ExpenseGroup.objects.get(id=8)
    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()

    mocked_patch = mock.MagicMock()
    mocker.patch('fyle_qbo_api.utils.patch_integration_settings', side_effect=mocked_patch)

    handle_quickbooks_error(exception=WrongParamsError(msg='Some Parameters are wrong', response=json.dumps({'error': 'invalid_grant'})), expense_group=expense_group, task_log=task_log, export_type='Bill')

    qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

    assert qbo_credentials.refresh_token == None
    assert qbo_credentials.is_expired == True
    assert task_log.quickbooks_errors['error'] == 'invalid_grant'

    args, kwargs = mocked_patch.call_args

    assert args[0] == expense_group.workspace_id
    assert kwargs['is_token_expired'] == True

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


def test_handle_qbo_invalid_token_error(db):
    # Get an expense group for testing
    expense_group = ExpenseGroup.objects.get(id=8)

    # Delete any existing invalid token errors for this workspace
    Error.objects.filter(
        workspace_id=expense_group.workspace_id,
        error_title='QuickBooks Online Connection Expired',
        is_resolved=False
    ).delete()

    # Call the function
    handle_qbo_invalid_token_error(expense_group)

    # Verify that a new error was created with correct details
    error = Error.objects.get(
        workspace_id=expense_group.workspace_id,
        error_title='QuickBooks Online Connection Expired',
        is_resolved=False
    )

    assert error.type == 'QBO_ERROR'
    assert error.error_detail == 'Your QuickBooks Online connection had expired during the previous export. Please click \'Export\' to retry exporting your expenses.'
    assert error.expense_group == expense_group

    # Test that calling again doesn't create duplicate error
    handle_qbo_invalid_token_error(expense_group)
    error_count = Error.objects.filter(
        workspace_id=expense_group.workspace_id,
        error_title='QuickBooks Online Connection Expired',
        is_resolved=False
    ).count()
    assert error_count == 1


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

    expenses = Expense.objects.filter(fund_source='PERSONAL', org_id='or79Cob97KSh').all()
    for expense in expenses:
        expense.paid_on_qbo = True
        expense.paid_on_fyle = False
        expense.workspace_id = workspace_id
        expense.save()

    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=workspace_id)

    reimbursement = Reimbursement.objects.filter(workspace_id=workspace_id).first()
    reimbursement.state = 'PENDING'
    reimbursement.save()

    process_reimbursements(workspace_id)

    reimbursement = Reimbursement.objects.filter(workspace_id=workspace_id).count()

    assert reimbursement == 1


def test_sync_accounts(mocker, db):
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.sync_accounts', return_value=None)
    old_accounts = DestinationAttribute.objects.filter(attribute_type='ACCOUNT', workspace_id=3).count()
    assert old_accounts == 63

    sync_accounts(3)
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

    schedule_credit_card_purchase_creation(workspace_id, [17], False, 1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False)

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

    schedule_bills_creation(workspace_id, [23], False, 1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False)

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

    schedule_cheques_creation(workspace_id, [23], False, 1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False)

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

    schedule_qbo_expense_creation(workspace_id, [23], False, 1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False)

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

    schedule_journal_entry_creation(workspace_id, [23], False, 1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False)

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    assert task_log.type == 'CREATING_JOURNAL_ENTRY'


def test_schedule_creation_with_no_expense_groups(db):
    workspace_id_4 = 4
    workspace_id_3 = 3

    expense_group_23 = ExpenseGroup.objects.get(id=23)
    expense_group_23.exported_at = django_timezone.now()
    expense_group_23.save()

    expense_group_17 = ExpenseGroup.objects.get(id=17)
    expense_group_17.exported_at = django_timezone.now()
    expense_group_17.save()

    initial_task_log_count_ws4 = TaskLog.objects.filter(workspace_id=workspace_id_4).count()
    initial_task_log_count_ws3 = TaskLog.objects.filter(workspace_id=workspace_id_3).count()

    schedule_bills_creation(workspace_id_4, [23], False, 1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False)
    assert TaskLog.objects.filter(workspace_id=workspace_id_4).count() == initial_task_log_count_ws4

    schedule_cheques_creation(workspace_id_4, [23], False, 1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False)
    assert TaskLog.objects.filter(workspace_id=workspace_id_4).count() == initial_task_log_count_ws4

    schedule_journal_entry_creation(workspace_id_4, [23], False, 1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False)
    assert TaskLog.objects.filter(workspace_id=workspace_id_4).count() == initial_task_log_count_ws4

    schedule_credit_card_purchase_creation(workspace_id_3, [17], False, 1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False)
    assert TaskLog.objects.filter(workspace_id=workspace_id_3).count() == initial_task_log_count_ws3

    schedule_qbo_expense_creation(workspace_id_4, [23], False, 1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False)
    assert TaskLog.objects.filter(workspace_id=workspace_id_4).count() == initial_task_log_count_ws4


def test_skipping_bill_payment(mocker, db):
    mocker.patch('apps.quickbooks_online.tasks.load_attachments', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.Reimbursements.sync', return_value=None)
    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=[])
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
        expense.previous_export_state = 'ERROR'
        expense.save()

    expense_group.expenses.set(expenses)
    expense_group.save()

    create_bill(expense_group.id, task_log.id, False, True)

    bill = Bill.objects.last()
    task_log = TaskLog.objects.get(id=task_log.id)
    task_log.expense_group = bill.expense_group
    task_log.save()

    reimbursements = data['reimbursements']

    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=workspace_id)

    task_log = TaskLog.objects.create(workspace_id=workspace_id, type='CREATING_BILL_PAYMENT', task_id='PAYMENT_{}'.format(bill.expense_group.id), status='FAILED')
    updated_at = task_log.updated_at
    create_bill_payment(workspace_id)

    task_log = TaskLog.objects.get(workspace_id=workspace_id, type='CREATING_BILL_PAYMENT', task_id='PAYMENT_{}'.format(bill.expense_group.id))
    assert task_log.updated_at == updated_at

    now = django_timezone.now()
    updated_at = now - timedelta(days=25)
    # Update created_at to more than 2 months ago (more than 60 days)
    TaskLog.objects.filter(task_id='PAYMENT_{}'.format(bill.expense_group.id)).update(
        created_at=now - timedelta(days=61),  # More than 2 months ago
        updated_at=updated_at  # Updated within the last 1 month
    )

    task_log = TaskLog.objects.get(task_id='PAYMENT_{}'.format(bill.expense_group.id))

    TaskLog.objects.filter(id=task_log.id).update(created_at=now - timedelta(days=70), updated_at=now - timedelta(days=70))
    task_log.refresh_from_db()
    create_bill_payment(workspace_id)

    updated_at = now - timedelta(days=25)
    # Update created_at to between 1 and 2 months ago (between 30 and 60 days)
    TaskLog.objects.filter(task_id='PAYMENT_{}'.format(bill.expense_group.id)).update(
        created_at=now - timedelta(days=45),  # Between 1 and 2 months ago
        updated_at=updated_at  # Updated within the last 1 month
    )
    create_bill_payment(workspace_id)


def test_get_or_create_error_with_expense_group_create_new(db):
    """
    Test creating a new error record
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.get(id=14)

    expense_attribute = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='EMPLOYEE',
        display_name='Employee',
        value='john.doe@fyle.in',
        source_id='123'
    )

    error, created = Error.get_or_create_error_with_expense_group(
        expense_group,
        expense_attribute
    )

    assert created == True
    assert error.workspace_id == workspace_id
    assert error.type == 'EMPLOYEE_MAPPING'
    assert error.error_title == 'john.doe@fyle.in'
    assert error.error_detail == 'Employee mapping is missing'
    assert error.is_resolved == False
    assert error.mapping_error_expense_group_ids == [expense_group.id]


def test_get_or_create_error_with_expense_group_update_existing(db):
    """
    Test updating an existing error record with new expense group ID
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.get(id=14)

    expense_attribute = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='EMPLOYEE',
        display_name='Employee',
        value='john.doe@fyle.in',
        source_id='123'
    )

    # Create initial error
    error1, _ = Error.get_or_create_error_with_expense_group(
        expense_group,
        expense_attribute
    )

    # Get another expense group
    expense_group2 = ExpenseGroup.objects.get(id=15)

    # Try to create error with same attribute but different expense group
    error2, created2 = Error.get_or_create_error_with_expense_group(
        expense_group2,
        expense_attribute
    )

    assert created2 == False
    assert error2.id == error1.id
    assert set(error2.mapping_error_expense_group_ids) == {expense_group.id, expense_group2.id}


def test_get_or_create_error_with_expense_group_category_mapping(db):
    """
    Test creating category mapping error
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.get(id=14)

    category_attribute = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        display_name='Category',
        value='Travel Test',
        source_id='456'
    )

    error, created = Error.get_or_create_error_with_expense_group(
        expense_group,
        category_attribute
    )

    assert created == True
    assert error.type == 'CATEGORY_MAPPING'
    assert error.error_title == 'Travel Test'
    assert error.error_detail == 'Category mapping is missing'
    assert error.mapping_error_expense_group_ids == [expense_group.id]


def test_get_or_create_error_with_expense_group_duplicate_expense_group(db):
    """
    Test that adding same expense group ID twice doesn't create duplicate
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.get(id=14)

    expense_attribute = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='EMPLOYEE',
        display_name='Employee',
        value='john.doe@fyle.in',
        source_id='123'
    )

    # Create initial error
    error1, _ = Error.get_or_create_error_with_expense_group(
        expense_group,
        expense_attribute
    )

    # Try to add same expense group again
    error2, created2 = Error.get_or_create_error_with_expense_group(
        expense_group,
        expense_attribute
    )

    assert created2 == False
    assert error2.id == error1.id
    assert len(error2.mapping_error_expense_group_ids) == 1
    assert error2.mapping_error_expense_group_ids == [expense_group.id]


def test_get_or_create_error_with_expense_group_tax_mapping(db):
    """
    Test creating tax mapping error
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.get(id=14)

    tax_attribute = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='TAX_GROUP',
        value='GST 10%',
        source_id='789',
        display_name='Tax Group'
    )

    error, created = Error.get_or_create_error_with_expense_group(
        expense_group,
        tax_attribute
    )

    assert created == True
    assert error.type == 'TAX_MAPPING'
    assert error.error_title == 'GST 10%'
    assert error.error_detail == 'Tax Group mapping is missing'
    assert error.mapping_error_expense_group_ids == [expense_group.id]
    assert error.workspace_id == workspace_id
    assert error.is_resolved == False


def test_handle_skipped_exports(mocker, db):
    mock_post_summary = mocker.patch('apps.quickbooks_online.queue.post_accounting_export_summary_for_skipped_exports', return_value=None)
    mock_update_last_export = mocker.patch('apps.quickbooks_online.queue.update_last_export_details')
    mock_logger = mocker.patch('apps.quickbooks_online.queue.logger')
    mocker.patch('apps.quickbooks_online.actions.patch_integration_settings', return_value=None)
    mocker.patch('apps.quickbooks_online.actions.post_accounting_export_summary', return_value=None)

    # Create or get two expense groups
    eg1 = ExpenseGroup.objects.create(workspace_id=1, fund_source='PERSONAL')
    eg2 = ExpenseGroup.objects.create(workspace_id=1, fund_source='PERSONAL')
    expense_groups = ExpenseGroup.objects.filter(id__in=[eg1.id, eg2.id])

    # Create a dummy error
    error = Error.objects.create(
        workspace_id=1,
        type='EMPLOYEE_MAPPING',
        expense_group=eg1,
        repetition_count=5,
        is_resolved=False,
        error_title='Test Error',
        error_detail='Test error detail',
    )

    # Case 1: triggered_by is DIRECT_EXPORT, not last export
    skip_export_count = 0
    result = handle_skipped_exports(
        expense_groups=expense_groups,
        index=0,
        skip_export_count=skip_export_count,
        error=error,
        expense_group=eg1,
        triggered_by=ExpenseImportSourceEnum.DIRECT_EXPORT
    )
    assert result == 1
    mock_post_summary.assert_called_once_with(eg1, eg1.workspace_id, is_mapping_error=False)
    mock_update_last_export.assert_not_called()
    mock_logger.info.assert_called()

    mock_post_summary.reset_mock()
    mock_update_last_export.reset_mock()
    mock_logger.reset_mock()

    # Case 2: last export, skip_export_count == total_count-1, should call update_last_export_details
    skip_export_count = 1
    result = handle_skipped_exports(
        expense_groups=expense_groups,
        index=1,
        skip_export_count=skip_export_count,
        error=None,
        expense_group=eg2,
        triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC
    )
    assert result == 2
    mock_post_summary.assert_not_called()
    mock_update_last_export.assert_called_once_with(eg2.workspace_id)
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_validate_for_skipping_payment_all_branches(db):
    # Setup
    workspace_id = 3
    expense_group = ExpenseGroup.objects.create(workspace_id=workspace_id)
    bill = Bill.objects.create(expense_group=expense_group, accounts_payable_id='ap', vendor_id='v', transaction_date=django_timezone.now().date(), currency='USD', private_note='note')
    now = django_timezone.now()
    task_id = f'PAYMENT_{expense_group.id}'

    # Case 1: No TaskLog exists
    assert validate_for_skipping_payment(bill, workspace_id) is False

    # Case 2: TaskLog created >2 months ago
    task_log = TaskLog.objects.create(
        workspace_id=workspace_id,
        type='CREATING_BILL_PAYMENT',
        task_id=task_id,
        expense_group=expense_group,
        status='READY'
    )
    TaskLog.objects.filter(id=task_log.id).update(created_at=now - timedelta(days=70), updated_at=now - timedelta(days=70))
    task_log.refresh_from_db()
    with mock.patch('django.utils.timezone.now', return_value=now):
        assert validate_for_skipping_payment(bill, workspace_id) is True
        bill.refresh_from_db()
        assert bill.is_retired is True

    # Case 3: TaskLog created between 1 and 2 months ago, updated within last month
    task_log.created_at = now - timedelta(days=45)
    task_log.updated_at = now - timedelta(days=10)
    task_log.save()
    bill.is_retired = False
    bill.save()
    with mock.patch('django.utils.timezone.now', return_value=now):
        assert validate_for_skipping_payment(bill, workspace_id) is True
        bill.refresh_from_db()
        assert bill.is_retired is False  # Should not be set in this branch

    # Case 4: TaskLog created <1 month ago, updated within last week
    task_log.created_at = now - timedelta(days=10)
    task_log.updated_at = now - timedelta(days=3)
    task_log.save()
    with mock.patch('django.utils.timezone.now', return_value=now):
        assert validate_for_skipping_payment(bill, workspace_id) is True

    # Case 5: TaskLog created <1 month ago, updated more than a week ago
    task_log.created_at = now - timedelta(days=10)
    task_log.updated_at = now - timedelta(days=10)
    task_log.save()
    with mock.patch('django.utils.timezone.now', return_value=now):
        assert validate_for_skipping_payment(bill, workspace_id) is True


@pytest.mark.django_db()
def test_create_journal_entry_task_log_does_not_exist(mocker, db):
    """
    Test create_journal_entry when TaskLog.DoesNotExist is raised
    Case: TaskLog with given task_log_id does not exist
    """
    with pytest.raises(TaskLog.DoesNotExist):
        create_journal_entry(1, 99999, True, False)


@pytest.mark.django_db()
def test_create_expense_report_task_log_does_not_exist(mocker, db):
    """
    Test create_expense_report when TaskLog.DoesNotExist is raised
    Case: TaskLog with given task_log_id does not exist
    """
    with pytest.raises(TaskLog.DoesNotExist):
        create_qbo_expense(1, 99999, True, False)


@pytest.mark.django_db()
def test_create_bill_task_log_does_not_exist(mocker, db):
    """
    Test create_bill when TaskLog.DoesNotExist is raised
    Case: TaskLog with given task_log_id does not exist
    """
    with pytest.raises(TaskLog.DoesNotExist):
        create_bill(1, 99999, True, False)


@pytest.mark.django_db()
def test_create_credit_card_charge_task_log_does_not_exist(mocker, db):
    """
    Test create_credit_card_charge when TaskLog.DoesNotExist is raised
    Case: TaskLog with given task_log_id does not exist
    """
    with pytest.raises(TaskLog.DoesNotExist):
        create_credit_card_purchase(1, 99999, True, False)
