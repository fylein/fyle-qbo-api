import json
import logging
import traceback
from datetime import datetime

from django.db import transaction
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping, ExpenseAttribute, Mapping
from fyle_integrations_platform_connector import PlatformConnector
from qbosdk.exceptions import InvalidTokenError, WrongParamsError

from apps.fyle.models import Expense, ExpenseGroup, Reimbursement
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.actions import update_last_export_details
from apps.quickbooks_online.exceptions import handle_qbo_exceptions
from apps.quickbooks_online.models import (
    Bill,
    BillLineitem,
    BillPayment,
    BillPaymentLineitem,
    Cheque,
    ChequeLineitem,
    CreditCardPurchase,
    CreditCardPurchaseLineitem,
    JournalEntry,
    JournalEntryLineitem,
    QBOExpense,
    QBOExpenseLineitem,
)
from apps.quickbooks_online.utils import QBOConnector
from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import FyleCredential, QBOCredential, WorkspaceGeneralSettings
from fyle_qbo_api.exceptions import BulkError

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def resolve_errors_for_exported_expense_group(expense_group: ExpenseGroup):
    """
    Resolve errors for exported expense group
    :param expense_group: Expense group
    """
    Error.objects.filter(workspace_id=expense_group.workspace_id, expense_group=expense_group, is_resolved=False).update(is_resolved=True)


def get_or_create_misc_vendor(debit_card_expense: bool, qbo_connection: QBOConnector):
    if debit_card_expense:
        vendor = qbo_connection.get_or_create_vendor('Debit Card Misc', create=True)
    else:
        vendor = qbo_connection.get_or_create_vendor('Credit Card Misc', create=True)

    return vendor


def get_or_create_credit_card_or_debit_card_vendor(workspace_id: int, merchant: str, debit_card_expense: bool, general_settings: WorkspaceGeneralSettings):
    """
    Get or create car default vendor
    :param workspace_id: Workspace Id
    :param merchant: Fyle Expense Merchant
    :return:
    """
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    vendor = None

    if merchant:
        try:
            vendor = qbo_connection.get_or_create_vendor(merchant, create=False)
        except WrongParamsError as bad_request:
            logger.error(bad_request.response)

        if not vendor:
            if general_settings.auto_create_merchants_as_vendors:
                try:
                    vendor = qbo_connection.get_or_create_vendor(merchant, create=True)
                except WrongParamsError as bad_request:
                    logger.error(bad_request.response)
            if not vendor:
                vendor = get_or_create_misc_vendor(debit_card_expense, qbo_connection)

    else:
        vendor = get_or_create_misc_vendor(debit_card_expense, qbo_connection)

    return vendor


def load_attachments(qbo_connection: QBOConnector, ref_id: str, ref_type: str, expense_group: ExpenseGroup):
    """
    Get attachments from fyle
    :param qbo_connection: QBO Connection
    :param ref_id: object id
    :param ref_type: type of object
    :param expense_group: Expense group
    """
    try:
        fyle_credentials = FyleCredential.objects.get(workspace_id=expense_group.workspace_id)
        file_ids = expense_group.expenses.values_list('file_ids', flat=True)
        platform = PlatformConnector(fyle_credentials)

        files_list = []
        attachments = []
        for file_id in file_ids:
            if file_id:
                for id in file_id:
                    file_object = {'id': id}
                    files_list.append(file_object)

        if files_list:
            attachments = platform.files.bulk_generate_file_urls(files_list)

        qbo_connection.post_attachments(ref_id, ref_type, attachments)

    except Exception:
        error = traceback.format_exc()
        logger.info('Attachment failed for expense group id %s / workspace id %s \n Error: %s', expense_group.id, expense_group.workspace_id, {'error': error})


def create_or_update_employee_mapping(expense_group: ExpenseGroup, qbo_connection: QBOConnector, auto_map_employees_preference: str):
    try:
        vendor_mapping = EmployeeMapping.objects.get(source_employee__value=expense_group.description.get('employee_email'), workspace_id=expense_group.workspace_id).destination_vendor
        if not vendor_mapping:
            raise EmployeeMapping.DoesNotExist
    except EmployeeMapping.DoesNotExist:
        source_employee = ExpenseAttribute.objects.get(workspace_id=expense_group.workspace_id, attribute_type='EMPLOYEE', value=expense_group.description.get('employee_email'))

        try:
            if auto_map_employees_preference == 'EMAIL':
                filters = {'detail__email__iexact': source_employee.value, 'attribute_type': 'VENDOR'}

            else:
                filters = {'value__iexact': source_employee.detail['full_name'], 'attribute_type': 'VENDOR'}
            filters['active'] = True

            entity = DestinationAttribute.objects.filter(workspace_id=expense_group.workspace_id, **filters).first()

            if entity is None:
                entity: DestinationAttribute = qbo_connection.get_or_create_vendor(vendor_name=source_employee.detail['full_name'], email=source_employee.value, create=True)

            if entity:
                existing_employee_mapping = EmployeeMapping.objects.filter(source_employee=source_employee).first()

                destination = {}
                if existing_employee_mapping:
                    destination['destination_employee_id'] = existing_employee_mapping.destination_employee_id
                    destination['destination_card_account_id'] = existing_employee_mapping.destination_card_account_id

                mapping = EmployeeMapping.create_or_update_employee_mapping(source_employee_id=source_employee.id, destination_vendor_id=entity.id, workspace=expense_group.workspace, **destination)

                mapping.source_employee.auto_mapped = True
                mapping.source_employee.save()

                mapping.destination_vendor.auto_created = True
                mapping.destination_vendor.save()
                return
        except WrongParamsError as bad_request:
            logger.error(bad_request.response)

            error_response = json.loads(bad_request.response)['Fault']['Error'][0]

            # This error code comes up when the vendor or employee already exists
            if error_response['code'] == '6240':
                logger.error('Destination Attribute with value %s not found in workspace %s', source_employee.detail['full_name'], expense_group.workspace_id)
                if source_employee:
                    Error.objects.update_or_create(
                        workspace_id=expense_group.workspace_id, expense_attribute=source_employee, defaults={'type': 'EMPLOYEE_MAPPING', 'error_title': source_employee.value, 'error_detail': 'Employee mapping is missing', 'is_resolved': False}
                    )

            raise BulkError('Mappings are missing', [{'row': None, 'expense_group_id': expense_group.id, 'value': expense_group.description.get('employee_email'), 'type': 'Employee Mapping', 'message': 'Employee mapping not found'}])


@handle_qbo_exceptions()
def create_bill(expense_group, task_log_id, last_export: bool):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(expense_group.workspace_id)

    qbo_connection = QBOConnector(qbo_credentials, expense_group.workspace_id)

    if expense_group.fund_source == 'PERSONAL' and general_settings.auto_map_employees and general_settings.auto_create_destination_entity and general_settings.auto_map_employees != 'EMPLOYEE_CODE':
        create_or_update_employee_mapping(expense_group, qbo_connection, general_settings.auto_map_employees)

    __validate_expense_group(expense_group, general_settings)

    with transaction.atomic():
        bill_object = Bill.create_bill(expense_group)

        bill_lineitems_objects = BillLineitem.create_bill_lineitems(expense_group, general_settings)

        created_bill = qbo_connection.post_bill(bill_object, bill_lineitems_objects)

        task_log.detail = created_bill
        task_log.bill = bill_object
        task_log.quickbooks_errors = None
        task_log.status = 'COMPLETE'
        task_log.save()

        expense_group.exported_at = datetime.now()
        expense_group.response_logs = created_bill
        expense_group.save()

        resolve_errors_for_exported_expense_group(expense_group)

    load_attachments(qbo_connection, created_bill['Bill']['Id'], 'Bill', expense_group)

    if last_export:
        update_last_export_details(expense_group.workspace_id)


def __validate_expense_group(expense_group: ExpenseGroup, general_settings: WorkspaceGeneralSettings):  # noqa: C901
    bulk_errors = []
    row = 0

    general_mapping = None

    try:
        general_mapping = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
    except GeneralMapping.DoesNotExist:
        bulk_errors.append({'row': None, 'expense_group_id': expense_group.id, 'value': 'bank account', 'type': 'General Mapping', 'message': 'General mapping not found'})

    if general_settings.corporate_credit_card_expenses_object and general_settings.corporate_credit_card_expenses_object == 'BILL' and expense_group.fund_source == 'CCC':
        if general_mapping:
            if not (general_mapping.default_ccc_vendor_id or general_mapping.default_ccc_vendor_name):
                bulk_errors.append({'row': None, 'expense_group_id': expense_group.id, 'value': expense_group.description.get('employee_email'), 'type': 'General Mapping', 'message': 'Default Credit Card Vendor not found'})

    if general_mapping and not (general_mapping.accounts_payable_id or general_mapping.accounts_payable_name):
        if (general_settings.reimbursable_expenses_object == 'BILL' or general_settings.corporate_credit_card_expenses_object == 'BILL') or (
            general_settings.reimbursable_expenses_object == 'JOURNAL ENTRY' and general_settings.employee_field_mapping == 'VENDOR' and expense_group.fund_source == 'PERSONAL'
        ):
            bulk_errors.append({'row': None, 'expense_group_id': expense_group.id, 'value': 'Accounts Payable', 'type': 'General Mapping', 'message': 'Accounts Payable not found'})

    if (
        general_mapping
        and not (general_mapping.bank_account_id or general_mapping.bank_account_name)
        and ((general_settings.reimbursable_expenses_object == 'CHECK' or (general_settings.reimbursable_expenses_object == 'JOURNAL ENTRY' and general_settings.employee_field_mapping == 'EMPLOYEE' and expense_group.fund_source == 'PERSONAL')))
    ):
        bulk_errors.append({'row': None, 'expense_group_id': expense_group.id, 'value': 'Bank Account', 'type': 'General Mapping', 'message': 'Bank Account not found'})

    if general_mapping and not (general_mapping.qbo_expense_account_id or general_mapping.qbo_expense_account_name) and general_settings.reimbursable_expenses_object == 'EXPENSE':
        bulk_errors.append({'row': None, 'expense_group_id': expense_group.id, 'value': 'Expense Payment Account', 'type': 'General Mapping', 'message': 'Expense Payment Account not found'})

    if general_settings.corporate_credit_card_expenses_object == 'CREDIT CARD PURCHASE' or general_settings.corporate_credit_card_expenses_object == 'JOURNAL ENTRY':
        ccc_account_mapping: EmployeeMapping = EmployeeMapping.objects.filter(source_employee__value=expense_group.description.get('employee_email'), workspace_id=expense_group.workspace_id).first()

        ccc_account_id = None
        if ccc_account_mapping and ccc_account_mapping.destination_card_account:
            ccc_account_id = ccc_account_mapping.destination_card_account.destination_id
        elif general_mapping:
            ccc_account_id = general_mapping.default_ccc_account_id

        if not ccc_account_id:
            bulk_errors.append(
                {'row': None, 'expense_group_id': expense_group.id, 'value': expense_group.description.get('employee_email'), 'type': 'Employee / General Mapping', 'message': 'CCC account mapping / Default CCC account mapping not found'}
            )

    if general_settings.corporate_credit_card_expenses_object not in ('BILL', 'DEBIT CARD EXPENSE') and expense_group.fund_source == 'CCC':
        if not (general_mapping.default_ccc_account_id or general_mapping.default_ccc_account_name):
            bulk_errors.append({'row': None, 'expense_group_id': expense_group.id, 'value': 'Default Credit Card Account', 'type': 'General Mapping', 'message': 'Default Credit Card Account not found'})

    if general_settings.corporate_credit_card_expenses_object == 'DEBIT CARD EXPENSE' and expense_group.fund_source == 'CCC':
        if not (general_mapping.default_debit_card_account_id or general_mapping.default_debit_card_account_name):
            bulk_errors.append({'row': None, 'expense_group_id': expense_group.id, 'value': 'Default Debit Card Account', 'type': 'General Mapping', 'message': 'Default Debit Card Account not found'})

    if general_settings.import_tax_codes and not (general_mapping.default_tax_code_id or general_mapping.default_tax_code_name):
        bulk_errors.append({'row': None, 'expense_group_id': expense_group.id, 'value': 'Default Tax Code', 'type': 'General Mapping', 'message': 'Default Tax Code not found'})

    if not (
        expense_group.fund_source == 'CCC'
        and ((general_settings.corporate_credit_card_expenses_object in ('CREDIT CARD PURCHASE', 'DEBIT CARD EXPENSE') and general_settings.map_merchant_to_vendor) or general_settings.corporate_credit_card_expenses_object == 'BILL')
    ):

        employee_attribute = ExpenseAttribute.objects.filter(value=expense_group.description.get('employee_email'), workspace_id=expense_group.workspace_id, attribute_type='EMPLOYEE').first()

        try:
            entity = EmployeeMapping.objects.get(source_employee=employee_attribute, workspace_id=expense_group.workspace_id)

            if general_settings.employee_field_mapping == 'EMPLOYEE':
                entity = entity.destination_employee
            else:
                entity = entity.destination_vendor if entity.destination_vendor and entity.destination_vendor.active else None

            if not entity:
                raise EmployeeMapping.DoesNotExist
        except EmployeeMapping.DoesNotExist:
            bulk_errors.append({'row': None, 'expense_group_id': expense_group.id, 'value': expense_group.description.get('employee_email'), 'type': 'Employee Mapping', 'message': 'Employee mapping not found'})
            if employee_attribute:
                Error.objects.update_or_create(
                    workspace_id=expense_group.workspace_id, expense_attribute=employee_attribute, defaults={'type': 'EMPLOYEE_MAPPING', 'error_title': employee_attribute.value, 'error_detail': 'Employee mapping is missing', 'is_resolved': False}
                )

    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        category = lineitem.category if (lineitem.category == lineitem.sub_category or lineitem.sub_category == None) else '{0} / {1}'.format(lineitem.category, lineitem.sub_category)

        category_attribute = ExpenseAttribute.objects.filter(value=category, workspace_id=expense_group.workspace_id, attribute_type='CATEGORY').first()

        account = Mapping.objects.filter(source_type='CATEGORY', destination_type='ACCOUNT', source=category_attribute, workspace_id=expense_group.workspace_id).first()

        if not account:
            bulk_errors.append({'row': row, 'expense_group_id': expense_group.id, 'value': category, 'type': 'Category Mapping', 'message': 'Category Mapping not found'})

            if category_attribute:
                Error.objects.update_or_create(
                    workspace_id=expense_group.workspace_id, expense_attribute=category_attribute, defaults={'type': 'CATEGORY_MAPPING', 'error_title': category_attribute.value, 'error_detail': 'Category mapping is missing', 'is_resolved': False}
                )

        if general_settings.import_tax_codes and lineitem.tax_group_id:
            tax_group = ExpenseAttribute.objects.get(workspace_id=expense_group.workspace_id, attribute_type='TAX_GROUP', source_id=lineitem.tax_group_id)

            tax_code = Mapping.objects.filter(source_type='TAX_GROUP', destination_type='TAX_CODE', source__value=tax_group.value, workspace_id=expense_group.workspace_id).first()

            if not tax_code:
                bulk_errors.append({'row': row, 'expense_group_id': expense_group.id, 'value': tax_group.value, 'type': 'Tax Group Mapping', 'message': 'Tax Group Mapping not found'})

                if tax_group:
                    Error.objects.update_or_create(workspace_id=expense_group.workspace_id, expense_attribute=tax_group, defaults={'type': 'TAX_MAPPING', 'error_title': tax_group.value, 'error_detail': 'Tax mapping is missing', 'is_resolved': False})
        row = row + 1

    if bulk_errors:
        raise BulkError('Mappings are missing', bulk_errors)


@handle_qbo_exceptions()
def create_cheque(expense_group, task_log_id, last_export: bool):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(expense_group.workspace_id)

    qbo_connection = QBOConnector(qbo_credentials, expense_group.workspace_id)

    if general_settings.auto_map_employees and general_settings.auto_create_destination_entity:
        create_or_update_employee_mapping(expense_group, qbo_connection, general_settings.auto_map_employees)

    __validate_expense_group(expense_group, general_settings)

    with transaction.atomic():
        cheque_object = Cheque.create_cheque(expense_group)

        cheque_line_item_objects = ChequeLineitem.create_cheque_lineitems(expense_group, general_settings)

        created_cheque = qbo_connection.post_cheque(cheque_object, cheque_line_item_objects)

        task_log.detail = created_cheque
        task_log.cheque = cheque_object
        task_log.quickbooks_errors = None
        task_log.status = 'COMPLETE'

        task_log.save()

        expense_group.exported_at = datetime.now()
        expense_group.response_logs = created_cheque
        expense_group.save()

        resolve_errors_for_exported_expense_group(expense_group)

        load_attachments(qbo_connection, created_cheque['Purchase']['Id'], 'Purchase', expense_group)

    if last_export:
        update_last_export_details(expense_group.workspace_id)


@handle_qbo_exceptions()
def create_qbo_expense(expense_group, task_log_id, last_export: bool):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(expense_group.workspace_id)

    qbo_connection = QBOConnector(qbo_credentials, expense_group.workspace_id)

    if expense_group.fund_source == 'PERSONAL':
        if general_settings.auto_map_employees and general_settings.auto_create_destination_entity:
            create_or_update_employee_mapping(expense_group, qbo_connection, general_settings.auto_map_employees)

    else:
        merchant = expense_group.expenses.first().vendor
        get_or_create_credit_card_or_debit_card_vendor(expense_group.workspace_id, merchant, True, general_settings)

    __validate_expense_group(expense_group, general_settings)

    with transaction.atomic():
        qbo_expense_object = QBOExpense.create_qbo_expense(expense_group)

        qbo_expense_line_item_objects = QBOExpenseLineitem.create_qbo_expense_lineitems(expense_group, general_settings)

        created_qbo_expense = qbo_connection.post_qbo_expense(qbo_expense_object, qbo_expense_line_item_objects)

        task_log.detail = created_qbo_expense
        task_log.qbo_expense = qbo_expense_object
        task_log.quickbooks_errors = None
        task_log.status = 'COMPLETE'

        task_log.save()

        expense_group.exported_at = datetime.now()
        expense_group.response_logs = created_qbo_expense
        expense_group.save()

        resolve_errors_for_exported_expense_group(expense_group)

    load_attachments(qbo_connection, created_qbo_expense['Purchase']['Id'], 'Purchase', expense_group)

    if last_export:
        update_last_export_details(expense_group.workspace_id)


@handle_qbo_exceptions()
def create_credit_card_purchase(expense_group: ExpenseGroup, task_log_id, last_export: bool):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(expense_group.workspace_id)

    qbo_connection = QBOConnector(qbo_credentials, int(expense_group.workspace_id))

    if not general_settings.map_merchant_to_vendor:
        if general_settings.auto_map_employees and general_settings.auto_create_destination_entity and general_settings.auto_map_employees != 'EMPLOYEE_CODE':
            create_or_update_employee_mapping(expense_group, qbo_connection, general_settings.auto_map_employees)
    else:
        merchant = expense_group.expenses.first().vendor
        get_or_create_credit_card_or_debit_card_vendor(expense_group.workspace_id, merchant, False, general_settings)

    __validate_expense_group(expense_group, general_settings)

    with transaction.atomic():
        credit_card_purchase_object = CreditCardPurchase.create_credit_card_purchase(expense_group, general_settings.map_merchant_to_vendor)

        credit_card_purchase_lineitems_objects = CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(expense_group, general_settings)

        created_credit_card_purchase = qbo_connection.post_credit_card_purchase(credit_card_purchase_object, credit_card_purchase_lineitems_objects)

        task_log.detail = created_credit_card_purchase
        task_log.credit_card_purchase = credit_card_purchase_object
        task_log.quickbooks_errors = None
        task_log.status = 'COMPLETE'

        task_log.save()

        expense_group.exported_at = datetime.now()
        expense_group.response_logs = created_credit_card_purchase
        expense_group.save()

        resolve_errors_for_exported_expense_group(expense_group)

        load_attachments(qbo_connection, created_credit_card_purchase['Purchase']['Id'], 'Purchase', expense_group)

    if last_export:
        update_last_export_details(expense_group.workspace_id)


@handle_qbo_exceptions()
def create_journal_entry(expense_group, task_log_id, last_export: bool):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(expense_group.workspace_id)

    qbo_connection = QBOConnector(qbo_credentials, expense_group.workspace_id)

    if general_settings.auto_map_employees and general_settings.auto_create_destination_entity and general_settings.auto_map_employees != 'EMPLOYEE_CODE':
        create_or_update_employee_mapping(expense_group, qbo_connection, general_settings.auto_map_employees)

    __validate_expense_group(expense_group, general_settings)

    with transaction.atomic():
        entity_map = qbo_connection.create_entity_id_map(expense_group, general_settings)

        journal_entry_object = JournalEntry.create_journal_entry(expense_group)

        journal_entry_lineitems_objects = JournalEntryLineitem.create_journal_entry_lineitems(expense_group, general_settings, entity_map)

        created_journal_entry = qbo_connection.post_journal_entry(journal_entry_object, journal_entry_lineitems_objects, general_settings.je_single_credit_line)

        task_log.detail = created_journal_entry
        task_log.journal_entry = journal_entry_object
        task_log.quickbooks_errors = None
        task_log.status = 'COMPLETE'

        task_log.save()

        expense_group.exported_at = datetime.now()
        expense_group.response_logs = created_journal_entry
        expense_group.save()

        resolve_errors_for_exported_expense_group(expense_group)

    load_attachments(qbo_connection, created_journal_entry['JournalEntry']['Id'], 'JournalEntry', expense_group)

    if last_export:
        update_last_export_details(expense_group.workspace_id)


def check_expenses_reimbursement_status(expenses):
    all_expenses_paid = True

    for expense in expenses:
        reimbursement = Reimbursement.objects.filter(settlement_id=expense.settlement_id).first()

        if reimbursement.state != 'COMPLETE':
            all_expenses_paid = False

    return all_expenses_paid


@handle_qbo_exceptions(bill_payment=True)
def process_bill_payments(bill: Bill, workspace_id: int, task_log: TaskLog):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(qbo_credentials, workspace_id)

    with transaction.atomic():

        bill_payment_object = BillPayment.create_bill_payment(bill.expense_group)

        qbo_object_task_log = TaskLog.objects.get(expense_group=bill.expense_group)

        linked_transaction_id = qbo_object_task_log.detail['Bill']['Id']

        bill_payment_lineitems_objects = BillPaymentLineitem.create_bill_payment_lineitems(bill_payment_object.expense_group, linked_transaction_id)

        created_bill_payment = qbo_connection.post_bill_payment(bill_payment_object, bill_payment_lineitems_objects)

        bill.payment_synced = True
        bill.paid_on_qbo = True
        bill.save()

        task_log.detail = created_bill_payment
        task_log.bill_payment = bill_payment_object
        task_log.quickbooks_errors = None
        task_log.status = 'COMPLETE'

        task_log.save()


def create_bill_payment(workspace_id):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

    platform = PlatformConnector(fyle_credentials)
    platform.reimbursements.sync()

    bills = Bill.objects.filter(payment_synced=False, expense_group__workspace_id=workspace_id, expense_group__fund_source='PERSONAL').all()

    if bills:
        for bill in bills:
            expense_group_reimbursement_status = check_expenses_reimbursement_status(bill.expense_group.expenses.all())
            if expense_group_reimbursement_status:
                task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace_id, task_id='PAYMENT_{}'.format(bill.expense_group.id), defaults={'status': 'IN_PROGRESS', 'type': 'CREATING_BILL_PAYMENT'})
                process_bill_payments(bill, workspace_id, task_log)


def get_all_qbo_object_ids(qbo_objects):
    qbo_objects_details = {}

    expense_group_ids = [qbo_object.expense_group_id for qbo_object in qbo_objects]

    task_logs = TaskLog.objects.filter(expense_group_id__in=expense_group_ids).all()

    for task_log in task_logs:
        qbo_objects_details[task_log.expense_group.id] = {'expense_group': task_log.expense_group, 'qbo_object_id': task_log.detail['Bill']['Id']}

    return qbo_objects_details


def check_qbo_object_status(workspace_id):
    try:
        qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)

        qbo_connection = QBOConnector(qbo_credentials, workspace_id)

        bills = Bill.objects.filter(expense_group__workspace_id=workspace_id, paid_on_qbo=False, expense_group__fund_source='PERSONAL').all()

        if bills:
            bill_ids = get_all_qbo_object_ids(bills)

            for bill in bills:
                bill_object = qbo_connection.get_bill(bill_ids[bill.expense_group.id]['qbo_object_id'])

                if 'LinkedTxn' in bill_object:
                    line_items = BillLineitem.objects.filter(bill_id=bill.id)
                    for line_item in line_items:
                        expense = line_item.expense
                        expense.paid_on_qbo = True
                        expense.save()

                    bill.paid_on_qbo = True
                    bill.payment_synced = True
                    bill.save()
    except (WrongParamsError, InvalidTokenError) as exception:
        logger.info('QBO token expired workspace_id - %s %s', workspace_id, {'error': exception.response})


def process_reimbursements(workspace_id):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

    platform = PlatformConnector(fyle_credentials)
    platform.reimbursements.sync()

    reimbursements = Reimbursement.objects.filter(state='PENDING', workspace_id=workspace_id).all()
    reimbursement_ids = []

    if reimbursements:
        for reimbursement in reimbursements:
            expenses = Expense.objects.filter(settlement_id=reimbursement.settlement_id, fund_source='PERSONAL').all()
            paid_expenses = expenses.filter(paid_on_qbo=True)

            all_expense_paid = False
            if len(expenses):
                all_expense_paid = len(expenses) == len(paid_expenses)

            if all_expense_paid:
                reimbursement_ids.append(reimbursement.reimbursement_id)

    if reimbursement_ids:
        reimbursements_list = []
        for reimbursement_id in reimbursement_ids:
            reimbursement_object = {'id': reimbursement_id}
            reimbursements_list.append(reimbursement_object)

        platform.reimbursements.bulk_post_reimbursements(reimbursements_list)
        platform.reimbursements.sync()


def async_sync_accounts(workspace_id):
    try:
        qbo_credentials: QBOCredential = QBOCredential.get_active_qbo_credentials(workspace_id)

        qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
        qbo_connection.sync_accounts()
    except (WrongParamsError, InvalidTokenError) as exception:
        logger.info('QBO token expired workspace_id - %s %s', workspace_id, {'error': exception.response})
