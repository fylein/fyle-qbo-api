import logging
import json
import traceback
from typing import List
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q
from django_q.tasks import Chain
from django_q.models import Schedule

from qbosdk.exceptions import WrongParamsError

from fyle_accounting_mappings.models import Mapping, ExpenseAttribute, DestinationAttribute

from fyle_qbo_api.exceptions import BulkError

from apps.fyle.models import ExpenseGroup, Reimbursement, Expense
from apps.tasks.models import TaskLog
from apps.mappings.models import GeneralMapping
from apps.workspaces.models import QBOCredential, FyleCredential, WorkspaceGeneralSettings
from apps.fyle.utils import FyleConnector

from .models import Bill, BillLineitem, Cheque, ChequeLineitem, CreditCardPurchase, CreditCardPurchaseLineitem, \
    JournalEntry, JournalEntryLineitem, BillPayment, BillPaymentLineitem
from .utils import QBOConnector

logger = logging.getLogger(__name__)


def get_or_create_credit_card_vendor(workspace_id: int, merchant: str):
    """
    Get or create car default vendor
    :param workspace_id: Workspace Id
    :param merchant: Fyle Expense Merchant
    :return:
    """
    qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    vendor = None

    if merchant:
        try:
            vendor = qbo_connection.get_or_create_vendor(merchant, create=False)
        except WrongParamsError as bad_request:
            logger.error(bad_request.response)

    if not vendor:
        vendor = qbo_connection.get_or_create_vendor('Credit Card Misc', create=True)

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
        expense_ids = expense_group.expenses.values_list('expense_id', flat=True)
        fyle_connector = FyleConnector(fyle_credentials.refresh_token, expense_group.workspace_id)
        attachments = fyle_connector.get_attachments(expense_ids)
        qbo_connection.post_attachments(ref_id, ref_type, attachments)
    except Exception:
        error = traceback.format_exc()
        logger.error(
            'Attachment failed for expense group id %s / workspace id %s \n Error: %s',
            expense_group.id, expense_group.workspace_id, {'error': error}
        )


def create_or_update_employee_mapping(expense_group: ExpenseGroup, qbo_connection: QBOConnector,
                                      auto_map_employees_preference: str):
    try:
        Mapping.objects.get(
            destination_type='VENDOR',
            source_type='EMPLOYEE',
            source__value=expense_group.description.get('employee_email'),
            workspace_id=expense_group.workspace_id
        )
    except Mapping.DoesNotExist:
        source_employee = ExpenseAttribute.objects.get(
            workspace_id=expense_group.workspace_id,
            attribute_type='EMPLOYEE',
            value=expense_group.description.get('employee_email')
        )

        try:
            if auto_map_employees_preference == 'EMAIL':
                filters = {
                    'detail__email__iexact': source_employee.value,
                    'attribute_type': 'VENDOR'
                }

            else:
                filters = {
                    'value__iexact': source_employee.detail['full_name'],
                    'attribute_type': 'VENDOR'
                }

            entity = DestinationAttribute.objects.filter(
                workspace_id=expense_group.workspace_id,
                **filters
            ).first()

            if entity is None:
                entity: DestinationAttribute = qbo_connection.get_or_create_vendor(
                    vendor_name=source_employee.detail['full_name'],
                    email=source_employee.value,
                    create=True
                )

            mapping = Mapping.create_or_update_mapping(
                source_type='EMPLOYEE',
                source_value=expense_group.description.get('employee_email'),
                destination_type='VENDOR',
                destination_id=entity.destination_id,
                destination_value=entity.value,
                workspace_id=int(expense_group.workspace_id)
            )

            mapping.source.auto_mapped = True
            mapping.source.save()
        except WrongParamsError as bad_request:
            logger.error(bad_request.response)

            error_response = json.loads(bad_request.response)['Fault']['Error'][0]

            # This error code comes up when the vendor or employee already exists
            if error_response['code'] == '6240':
                logger.error(
                    'Destination Attribute with value %s not found in workspace %s',
                    source_employee.detail['full_name'],
                    expense_group.workspace_id
                )


def schedule_bills_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule bills creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, bill__id__isnull=True, exported_at__isnull=True
        ).all()

        chain = Chain()

        for expense_group in expense_groups:
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={
                    'status': 'ENQUEUED',
                    'type': 'CREATING_BILL'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.status = 'ENQUEUED'
                task_log.save()

            chain.append('apps.quickbooks_online.tasks.create_bill', expense_group, task_log.id)

        if chain.length():
            chain.run()


def create_bill(expense_group, task_log_id):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)

    try:
        qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

        qbo_connection = QBOConnector(qbo_credentials, expense_group.workspace_id)

        if expense_group.fund_source == 'PERSONAL' and general_settings.auto_map_employees \
                and general_settings.auto_create_destination_entity \
                and general_settings.auto_map_employees != 'EMPLOYEE_CODE':
            create_or_update_employee_mapping(expense_group, qbo_connection, general_settings.auto_map_employees)

        with transaction.atomic():
            __validate_expense_group(expense_group, general_settings)

            bill_object = Bill.create_bill(expense_group)

            bill_lineitems_objects = BillLineitem.create_bill_lineitems(expense_group)

            created_bill = qbo_connection.post_bill(bill_object, bill_lineitems_objects)

            load_attachments(qbo_connection, created_bill['Bill']['Id'], 'Bill', expense_group)

            task_log.detail = created_bill
            task_log.bill = bill_object
            task_log.status = 'COMPLETE'

            task_log.save()

            expense_group.exported_at = datetime.now()
            expense_group.save()

    except QBOCredential.DoesNotExist:
        logger.error(
            'QBO Credentials not found for workspace_id %s / expense group %s',
            expense_group.workspace_id,
            expense_group.id
        )
        detail = {
            'expense_group_id': expense_group.id,
            'message': 'QBO Account not connected'
        }
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except BulkError as exception:
        logger.error(exception.response)
        detail = exception.response
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except WrongParamsError as exception:
        logger.error(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save()
        logger.error('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)


def __validate_expense_group(expense_group: ExpenseGroup, general_settings: WorkspaceGeneralSettings):
    bulk_errors = []
    row = 0

    general_mapping = None

    try:
        general_mapping = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
    except GeneralMapping.DoesNotExist:
        bulk_errors.append({
            'row': None,
            'expense_group_id': expense_group.id,
            'value': 'bank account',
            'type': 'General Mapping',
            'message': 'General mapping not found'
        })

    if general_settings.corporate_credit_card_expenses_object and \
            general_settings.corporate_credit_card_expenses_object == 'BILL' and \
            expense_group.fund_source == 'CCC':
        if general_mapping:
            if not (general_mapping.default_ccc_vendor_id or general_mapping.default_ccc_vendor_name):
                bulk_errors.append({
                    'row': None,
                    'expense_group_id': expense_group.id,
                    'value': expense_group.description.get('employee_email'),
                    'type': 'General Mapping',
                    'message': 'Default Credit Card Vendor not found'
                })

    if general_settings.corporate_credit_card_expenses_object != 'BILL' and expense_group.fund_source == 'CCC':
        if not (general_mapping.default_ccc_account_id or general_mapping.default_ccc_account_name):
            bulk_errors.append({
                'row': None,
                'expense_group_id': expense_group.id,
                'value': 'Default Credit Card Account',
                'type': 'General Mapping',
                'message': 'Default Credit Card Account not found'
            })
    else:
        if not (general_settings.corporate_credit_card_expenses_object == 'CREDIT CARD PURCHASE'
                and general_settings.map_merchant_to_vendor and expense_group.fund_source == 'CCC'):
            try:
                Mapping.objects.get(
                    Q(destination_type='VENDOR') | Q(destination_type='EMPLOYEE'),
                    source_type='EMPLOYEE',
                    source__value=expense_group.description.get('employee_email'),
                    workspace_id=expense_group.workspace_id
                )
            except Mapping.DoesNotExist:
                bulk_errors.append({
                    'row': None,
                    'expense_group_id': expense_group.id,
                    'value': expense_group.description.get('employee_email'),
                    'type': 'Employee Mapping',
                    'message': 'Employee mapping not found'
                })

    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(
            lineitem.category, lineitem.sub_category)

        account = Mapping.objects.filter(
            source_type='CATEGORY',
            source__value=category,
            workspace_id=expense_group.workspace_id
        ).first()
        if not account:
            bulk_errors.append({
                'row': row,
                'expense_group_id': expense_group.id,
                'value': category,
                'type': 'Category Mapping',
                'message': 'Category Mapping not found'
            })

        row = row + 1

    if bulk_errors:
        raise BulkError('Mappings are missing', bulk_errors)


def schedule_cheques_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule cheque creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, cheque__id__isnull=True, exported_at__isnull=True
        ).all()

        chain = Chain()

        for expense_group in expense_groups:
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={
                    'status': 'ENQUEUED',
                    'type': 'CREATING_CHECK'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.status = 'ENQUEUED'
                task_log.save()

            chain.append('apps.quickbooks_online.tasks.create_cheque', expense_group, task_log.id)

        if chain.length():
            chain.run()


def create_cheque(expense_group, task_log_id):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)
    try:
        qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

        qbo_connection = QBOConnector(qbo_credentials, expense_group.workspace_id)

        if general_settings.auto_map_employees and general_settings.auto_create_destination_entity:
            create_or_update_employee_mapping(expense_group, qbo_connection, general_settings.auto_map_employees)

        with transaction.atomic():
            __validate_expense_group(expense_group, general_settings)

            cheque_object = Cheque.create_cheque(expense_group)

            cheque_line_item_objects = ChequeLineitem.create_cheque_lineitems(expense_group)

            created_cheque = qbo_connection.post_cheque(cheque_object, cheque_line_item_objects)

            load_attachments(qbo_connection, created_cheque['Purchase']['Id'], 'Purchase', expense_group)

            task_log.detail = created_cheque
            task_log.cheque = cheque_object
            task_log.status = 'COMPLETE'

            task_log.save()

            expense_group.exported_at = datetime.now()
            expense_group.save()

    except QBOCredential.DoesNotExist:
        logger.error(
            'QBO Credentials not found for workspace_id %s / expense group %s',
            expense_group.id,
            expense_group.workspace_id
        )
        detail = {
            'expense_group_id': expense_group.id,
            'message': 'QBO Account not connected'
        }
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except BulkError as exception:
        logger.error(exception.response)
        detail = exception.response
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except WrongParamsError as exception:
        logger.error(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save()
        logger.error('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)


def schedule_credit_card_purchase_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule credit card purchase creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, creditcardpurchase__id__isnull=True,
            exported_at__isnull=True
        ).all()

        chain = Chain()

        for expense_group in expense_groups:
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={
                    'status': 'ENQUEUED',
                    'type': 'CREATING_CREDIT_CARD_PURCHASE'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.status = 'ENQUEUED'
                task_log.save()

            chain.append('apps.quickbooks_online.tasks.create_credit_card_purchase', expense_group, task_log.id)

        if chain.length():
            chain.run()


def create_credit_card_purchase(expense_group: ExpenseGroup, task_log_id):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)

    try:
        qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

        qbo_connection = QBOConnector(qbo_credentials, int(expense_group.workspace_id))

        if not general_settings.map_merchant_to_vendor:
            if general_settings.auto_map_employees and general_settings.auto_create_destination_entity \
                    and general_settings.auto_map_employees != 'EMPLOYEE_CODE':
                create_or_update_employee_mapping(expense_group, qbo_connection, general_settings.auto_map_employees)
        else:
            merchant = expense_group.expenses.first().vendor
            get_or_create_credit_card_vendor(expense_group.workspace_id, merchant)

        with transaction.atomic():
            __validate_expense_group(expense_group, general_settings)

            credit_card_purchase_object = CreditCardPurchase.create_credit_card_purchase(
                expense_group, general_settings.map_merchant_to_vendor)

            credit_card_purchase_lineitems_objects = CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(
                expense_group
            )

            created_credit_card_purchase = qbo_connection.post_credit_card_purchase(
                credit_card_purchase_object, credit_card_purchase_lineitems_objects
            )

            load_attachments(qbo_connection, created_credit_card_purchase['Purchase']['Id'], 'Purchase', expense_group)

            task_log.detail = created_credit_card_purchase
            task_log.credit_card_purchase = credit_card_purchase_object
            task_log.status = 'COMPLETE'

            task_log.save()

            expense_group.exported_at = datetime.now()
            expense_group.save()

    except QBOCredential.DoesNotExist:
        logger.error(
            'QBO Credentials not found for workspace_id %s / expense group %s',
            expense_group.id,
            expense_group.workspace_id
        )
        detail = {
            'expense_group_id': expense_group.id,
            'message': 'QBO Account not connected'
        }
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except BulkError as exception:
        logger.error(exception.response)
        detail = exception.response
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except WrongParamsError as exception:
        logger.error(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save()
        logger.error('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)


def schedule_journal_entry_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule journal_entry creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, journalentry__id__isnull=True, exported_at__isnull=True
        ).all()

        chain = Chain()

        for expense_group in expense_groups:
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={
                    'status': 'ENQUEUED',
                    'type': 'CREATING_JOURNAL_ENTRY'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.status = 'ENQUEUED'
                task_log.save()

            chain.append('apps.quickbooks_online.tasks.create_journal_entry', expense_group, task_log.id)

        if chain.length():
            chain.run()


def create_journal_entry(expense_group, task_log_id):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)

    try:
        qbo_credentials = QBOCredential.objects.get(workspace_id=expense_group.workspace_id)

        qbo_connection = QBOConnector(qbo_credentials, expense_group.workspace_id)

        if general_settings.auto_map_employees and general_settings.auto_create_destination_entity \
                and general_settings.auto_map_employees != 'EMPLOYEE_CODE':
            create_or_update_employee_mapping(expense_group, qbo_connection, general_settings.auto_map_employees)

        with transaction.atomic():
            __validate_expense_group(expense_group, general_settings)

            journal_entry_object = JournalEntry.create_journal_entry(expense_group)

            journal_entry_lineitems_objects = JournalEntryLineitem.create_journal_entry_lineitems(
                expense_group
            )

            created_journal_entry = qbo_connection.post_journal_entry(journal_entry_object,
                                                                      journal_entry_lineitems_objects)

            load_attachments(qbo_connection, created_journal_entry['JournalEntry']['Id'], 'JournalEntry', expense_group)

            task_log.detail = created_journal_entry
            task_log.journal_entry = journal_entry_object
            task_log.status = 'COMPLETE'

            task_log.save()

            expense_group.exported_at = datetime.now()
            expense_group.save()

    except QBOCredential.DoesNotExist:
        logger.error(
            'QBO Credentials not found for workspace_id %s / expense group %s',
            expense_group.id,
            expense_group.workspace_id
        )
        detail = {
            'expense_group_id': expense_group.id,
            'message': 'QBO Account not connected'
        }
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except BulkError as exception:
        logger.error(exception.response)
        detail = exception.response
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except WrongParamsError as exception:
        logger.error(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save()
        logger.error('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)


def check_expenses_reimbursement_status(expenses):
    all_expenses_paid = True

    for expense in expenses:
        reimbursement = Reimbursement.objects.filter(settlement_id=expense.settlement_id).first()

        if reimbursement.state != 'COMPLETE':
            all_expenses_paid = False

    return all_expenses_paid


def create_bill_payment(workspace_id):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

    fyle_connector = FyleConnector(fyle_credentials.refresh_token, workspace_id)

    fyle_connector.sync_reimbursements()

    bills = Bill.objects.filter(
        payment_synced=False, expense_group__workspace_id=workspace_id,
        expense_group__fund_source='PERSONAL'
    ).all()

    if bills:
        for bill in bills:
            expense_group_reimbursement_status = check_expenses_reimbursement_status(
                bill.expense_group.expenses.all())
            if expense_group_reimbursement_status:
                task_log, _ = TaskLog.objects.update_or_create(
                    workspace_id=workspace_id,
                    task_id='PAYMENT_{}'.format(bill.expense_group.id),
                    defaults={
                        'status': 'IN_PROGRESS',
                        'type': 'CREATING_BILL_PAYMENT'
                    }
                )
                try:
                    with transaction.atomic():

                        bill_payment_object = BillPayment.create_bill_payment(bill.expense_group)

                        qbo_object_task_log = TaskLog.objects.get(expense_group=bill.expense_group)

                        linked_transaction_id = qbo_object_task_log.detail['Bill']['Id']

                        bill_payment_lineitems_objects = BillPaymentLineitem.create_bill_payment_lineitems(
                            bill_payment_object.expense_group, linked_transaction_id
                        )

                        qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)

                        qbo_connection = QBOConnector(qbo_credentials, workspace_id)

                        created_bill_payment = qbo_connection.post_bill_payment(
                            bill_payment_object, bill_payment_lineitems_objects
                        )

                        bill.payment_synced = True
                        bill.paid_on_qbo = True
                        bill.save()

                        task_log.detail = created_bill_payment
                        task_log.bill_payment = bill_payment_object
                        task_log.status = 'COMPLETE'

                        task_log.save()

                except QBOCredential.DoesNotExist:
                    logger.error(
                        'QBO Credentials not found for workspace_id %s / expense group %s',
                        workspace_id,
                        bill.expense_group
                    )
                    detail = {
                        'expense_group_id': bill.expense_group,
                        'message': 'QBO Account not connected'
                    }
                    task_log.status = 'FAILED'
                    task_log.detail = detail

                    task_log.save()

                except BulkError as exception:
                    logger.error(exception.response)
                    detail = exception.response
                    task_log.status = 'FAILED'
                    task_log.detail = detail

                    task_log.save()

                except WrongParamsError as exception:
                    logger.error(exception.response)
                    detail = json.loads(exception.response)
                    task_log.status = 'FAILED'
                    task_log.detail = detail

                    task_log.save()

                except Exception:
                    error = traceback.format_exc()
                    task_log.detail = {
                        'error': error
                    }
                    task_log.status = 'FATAL'
                    task_log.save()
                    logger.error(
                        'Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)


def schedule_bill_payment_creation(sync_fyle_to_qbo_payments, workspace_id):
    general_mappings: GeneralMapping = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    if general_mappings:
        if sync_fyle_to_qbo_payments and general_mappings.bill_payment_account_id:
            start_datetime = datetime.now()
            schedule, _ = Schedule.objects.update_or_create(
                func='apps.quickbooks_online.tasks.create_bill_payment',
                args='{}'.format(workspace_id),
                defaults={
                    'schedule_type': Schedule.MINUTES,
                    'minutes': 24 * 60,
                    'next_run': start_datetime
                }
            )
    if not sync_fyle_to_qbo_payments:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.quickbooks_online.tasks.create_bill_payment',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def get_all_qbo_object_ids(qbo_objects):
    qbo_objects_details = {}

    expense_group_ids = [qbo_object.expense_group_id for qbo_object in qbo_objects]

    task_logs = TaskLog.objects.filter(expense_group_id__in=expense_group_ids).all()

    for task_log in task_logs:
        qbo_objects_details[task_log.expense_group.id] = {
            'expense_group': task_log.expense_group,
            'qbo_object_id': task_log.detail['Bill']['Id']
        }

    return qbo_objects_details


def check_qbo_object_status(workspace_id):
    qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)

    qbo_connection = QBOConnector(qbo_credentials, workspace_id)

    bills = Bill.objects.filter(
        expense_group__workspace_id=workspace_id, paid_on_qbo=False, expense_group__fund_source='PERSONAL'
    ).all()

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


def schedule_qbo_objects_status_sync(sync_qbo_to_fyle_payments, workspace_id):
    if sync_qbo_to_fyle_payments:
        start_datetime = datetime.now()
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.quickbooks_online.tasks.check_qbo_object_status',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.quickbooks_online.tasks.check_qbo_object_status',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def process_reimbursements(workspace_id):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

    fyle_connector = FyleConnector(fyle_credentials.refresh_token, workspace_id)

    fyle_connector.sync_reimbursements()

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
        fyle_connector.post_reimbursement(reimbursement_ids)
        fyle_connector.sync_reimbursements()


def schedule_reimbursements_sync(sync_qbo_to_fyle_payments, workspace_id):
    if sync_qbo_to_fyle_payments:
        start_datetime = datetime.now() + timedelta(hours=12)
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.quickbooks_online.tasks.process_reimbursements',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.quickbooks_online.tasks.process_reimbursements',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()
