"""
QBO models
"""
from datetime import datetime
from typing import Dict, List

from django.conf import settings
from django.db import models

from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.mappings.models import GeneralMapping
from apps.workspaces.enums import ExportTypeEnum, SystemCommentEntityTypeEnum, SystemCommentIntentEnum, SystemCommentReasonEnum, SystemCommentSourceEnum
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from apps.workspaces.system_comments import add_system_comment
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping, ExpenseAttribute, Mapping, MappingSetting


def get_transaction_date(expense_group: ExpenseGroup) -> str:
    if 'spent_at' in expense_group.description and expense_group.description['spent_at']:
        return expense_group.description['spent_at']
    elif 'approved_at' in expense_group.description and expense_group.description['approved_at']:
        return expense_group.description['approved_at']
    elif 'verified_at' in expense_group.description and expense_group.description['verified_at']:
        return expense_group.description['verified_at']
    elif 'posted_at' in expense_group.description and expense_group.description['posted_at']:
        return expense_group.description['posted_at']
    elif 'last_spent_at' in expense_group.description and expense_group.description['last_spent_at']:
        return expense_group.description['last_spent_at']

    return datetime.now().strftime("%Y-%m-%d")


def get_expense_purpose(workspace_id, lineitem, category, workspace_general_settings) -> str:
    org_id = Workspace.objects.get(id=workspace_id).fyle_org_id
    memo_structure = workspace_general_settings.memo_structure

    details = {
        'employee_email': lineitem.employee_email,
        'employee_name': lineitem.employee_name,
        'card_number': '{0}'.format(lineitem.masked_corporate_card_number) if lineitem.masked_corporate_card_number else '',
        'merchant': '{0}'.format(lineitem.vendor) if lineitem.vendor else '',
        'category': '{0}'.format(category) if lineitem.category else '',
        'purpose': '{0}'.format(lineitem.purpose) if lineitem.purpose else '',
        'report_number': '{0}'.format(lineitem.claim_number),
        'spent_on': '{0}'.format(lineitem.spent_at.date()) if lineitem.spent_at else '',
        'expense_link': '{0}/app/admin/#/company_expenses?txnId={1}&org_id={2}'.format(settings.FYLE_EXPENSE_URL, lineitem.expense_id, org_id),
    }

    memo_parts = []
    for field in memo_structure:
        if field in details and details[field]:
            memo_parts.append(details[field])

    return ' - '.join(memo_parts)


def construct_private_note(expense_group: ExpenseGroup):
    expense = expense_group.expenses.first()
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)
    expense_type = 'Reimbursable'
    if expense_group.fund_source == 'CCC':
        expense_type = 'Corporate Card' if workspace_general_settings.corporate_credit_card_expenses_object == 'DEBIT CARD EXPENSE' else 'Credit card'
    merchant = ' spent on merchant {0}'.format(expense.vendor) if expense.vendor else ''
    spent_at = ' on {0} '.format(expense.spent_at.date()) if expense.spent_at else ''

    private_note = '{0} expense by {1}'.format(expense_type, expense.employee_email)
    if expense_group.expenses.count() == 1:
        private_note = '{0}{1}{2}'.format(private_note, merchant, spent_at)

    return private_note


def get_ccc_account_id(workspace_general_settings, general_mappings, expense, description, export_type='CREDIT_CARD_EXPENSE', system_comments: list = None):
    if workspace_general_settings.map_fyle_cards_qbo_account:
        ccc_account = Mapping.objects.filter(source_type='CORPORATE_CARD', source__source_id=expense.corporate_card_id, workspace_id=workspace_general_settings.workspace_id).first()
        if export_type == 'DEBIT_CARD_EXPENSE' and not ccc_account:
            return None

        if ccc_account:
            return ccc_account.destination.destination_id
        else:
            add_system_comment(
                system_comments=system_comments,
                source=SystemCommentSourceEnum.GET_CCC_ACCOUNT_ID,
                intent=SystemCommentIntentEnum.DEFAULT_VALUE_APPLIED,
                entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                workspace_id=workspace_general_settings.workspace_id,
                entity_id=expense.id,
                reason=SystemCommentReasonEnum.DEFAULT_CCC_ACCOUNT_APPLIED,
                info={'default_ccc_account_id': general_mappings.default_ccc_account_id, 'default_ccc_account_name': general_mappings.default_ccc_account_name},
                persist_without_export=False
            )
            return general_mappings.default_ccc_account_id
    else:
        ccc_account_mapping: EmployeeMapping = EmployeeMapping.objects.filter(source_employee__value=description.get('employee_email'), workspace_id=workspace_general_settings.workspace_id).first()
        if ccc_account_mapping and ccc_account_mapping.destination_card_account:
            add_system_comment(
                system_comments=system_comments,
                source=SystemCommentSourceEnum.GET_CCC_ACCOUNT_ID,
                intent=SystemCommentIntentEnum.EMPLOYEE_DEFAULT_VALUE_APPLIED,
                entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                workspace_id=workspace_general_settings.workspace_id,
                entity_id=expense.id,
                reason=SystemCommentReasonEnum.EMPLOYEE_CCC_ACCOUNT_APPLIED,
                info={'employee_ccc_account_id': ccc_account_mapping.destination_card_account.destination_id, 'employee_ccc_account_name': ccc_account_mapping.destination_card_account.display_name},
                persist_without_export=False
            )
            return ccc_account_mapping.destination_card_account.destination_id
        else:
            add_system_comment(
                system_comments=system_comments,
                source=SystemCommentSourceEnum.GET_CCC_ACCOUNT_ID,
                intent=SystemCommentIntentEnum.DEFAULT_VALUE_APPLIED,
                entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                workspace_id=workspace_general_settings.workspace_id,
                entity_id=expense.id,
                reason=SystemCommentReasonEnum.DEFAULT_CCC_ACCOUNT_APPLIED,
                info={'default_ccc_account_id': general_mappings.default_ccc_account_id, 'default_ccc_account_name': general_mappings.default_ccc_account_name},
                persist_without_export=False
            )
            return general_mappings.default_ccc_account_id


def get_class_id_or_none(expense_group: ExpenseGroup, lineitem: Expense):
    class_setting: MappingSetting = MappingSetting.objects.filter(workspace_id=expense_group.workspace_id, destination_field='CLASS').first()

    class_id = None

    if class_setting:
        if class_setting.source_field == 'PROJECT':
            source_value = lineitem.project
        elif class_setting.source_field == 'COST_CENTER':
            source_value = lineitem.cost_center
        else:
            attribute = ExpenseAttribute.objects.filter(attribute_type=class_setting.source_field, workspace_id=expense_group.workspace_id).first()
            source_value = lineitem.custom_properties.get(attribute.display_name, None)

        mapping: Mapping = Mapping.objects.filter(source_type=class_setting.source_field, destination_type='CLASS', source__value=source_value, workspace_id=expense_group.workspace_id).first()

        if mapping:
            class_id = mapping.destination.destination_id
    return class_id


def get_customer_id_or_none(expense_group: ExpenseGroup, lineitem: Expense):
    customer_setting: MappingSetting = MappingSetting.objects.filter(workspace_id=expense_group.workspace_id, destination_field='CUSTOMER').first()

    customer_id = None

    if customer_setting:
        if customer_setting.source_field == 'PROJECT':
            source_value = lineitem.project
        elif customer_setting.source_field == 'COST_CENTER':
            source_value = lineitem.cost_center
        else:
            attribute = ExpenseAttribute.objects.filter(attribute_type=customer_setting.source_field, workspace_id=expense_group.workspace_id).first()
            source_value = lineitem.custom_properties.get(attribute.display_name, None)

        mapping: Mapping = Mapping.objects.filter(source_type=customer_setting.source_field, destination_type='CUSTOMER', source__value=source_value, workspace_id=expense_group.workspace_id).first()

        if mapping:
            customer_id = mapping.destination.destination_id
    return customer_id


def get_tax_code_id_or_none(expense_group: ExpenseGroup, lineitem: Expense = None):
    tax_code = None
    mapping: Mapping = Mapping.objects.filter(source_type='TAX_GROUP', destination_type='TAX_CODE', source__source_id=lineitem.tax_group_id, workspace_id=expense_group.workspace_id).first()
    if mapping:
        tax_code = mapping.destination.destination_id

    return tax_code


def get_department_id_or_none(expense_group: ExpenseGroup, lineitem: Expense = None):
    department_setting: MappingSetting = MappingSetting.objects.filter(workspace_id=expense_group.workspace_id, destination_field='DEPARTMENT').first()

    department_id = None

    if department_setting:
        if lineitem:
            if department_setting.source_field == 'PROJECT':
                source_value = lineitem.project
            elif department_setting.source_field == 'COST_CENTER':
                source_value = lineitem.cost_center
            else:
                attribute = ExpenseAttribute.objects.filter(attribute_type=department_setting.source_field, workspace_id=expense_group.workspace_id).first()
                source_value = lineitem.custom_properties.get(attribute.display_name, None)
        else:
            source_value = expense_group.description[department_setting.source_field.lower()] if department_setting.source_field.lower() in expense_group.description else None

        mapping: Mapping = Mapping.objects.filter(source_type=department_setting.source_field, destination_type='DEPARTMENT', source__value=source_value, workspace_id=expense_group.workspace_id).first()

        if mapping:
            department_id = mapping.destination.destination_id
    return department_id


def get_category_mapping_and_detail_type(workspace_general_settings: WorkspaceGeneralSettings, category: str, workspace_id: int):
    # get the item-mapping if import_items is true
    if workspace_general_settings.import_items:
        qbo_item: Mapping = Mapping.objects.filter(source_type='CATEGORY', destination_type='ACCOUNT', destination__display_name='Item', source__value=category, workspace_id=workspace_id).first()
        # if qbo_item is found, return item and ItemBasedExpenseLineDetail as detail_type
        if qbo_item:
            return qbo_item, 'ItemBasedExpenseLineDetail'

    # else get the account-mapping and return the detail_type as AccountBasedExpenseLineDetail
    qbo_account: Mapping = Mapping.objects.filter(source_type='CATEGORY', destination_type='ACCOUNT', source__value=category, destination__display_name='Account', workspace_id=workspace_id).first()

    return qbo_account, 'AccountBasedExpenseLineDetail'


def get_credit_card_purchase_number(expense_group: ExpenseGroup, expense: Expense, expense_group_settings: ExpenseGroupSettings):
    if expense_group.expenses.count() > 1 and expense_group_settings.split_expense_grouping == 'MULTIPLE_LINE_ITEM' and 'bank_transaction_id' in expense_group.description:
        return expense_group.description['bank_transaction_id']
    else:
        return expense.expense_number


def get_fyle_identifier_number(expense_group: ExpenseGroup):
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=expense_group.workspace_id)

    group_fields = expense_group_settings.corporate_credit_card_expense_group_fields
    if expense_group.fund_source == 'PERSONAL':
        group_fields = expense_group_settings.reimbursable_expense_group_fields

    group_by_field = 'claim_number'
    if 'expense_id' in group_fields:
        group_by_field = 'expense_number'

    group_by_field_value = expense_group.expenses.first().__getattribute__(group_by_field)
    return group_by_field_value


def _get_export_number(expense_group: ExpenseGroup, exported_module: "Bill | JournalEntry", field_name: str) -> str:
    key = get_fyle_identifier_number(expense_group)
    exported_module_qs = exported_module.objects.filter(
        **{
            f"{field_name}__icontains": key,
            "expense_group__workspace_id": expense_group.workspace_id,
        }
    )
    count = exported_module_qs.count()
    return f"{key} - {count}" if count else key


def get_bill_number(expense_group: ExpenseGroup) -> str:
    return _get_export_number(expense_group, Bill, "bill_number")


def get_journal_number(expense_group: ExpenseGroup) -> str:
    return _get_export_number(expense_group, JournalEntry, "journal_number")


class Bill(models.Model):
    """
    QBO Bill
    """

    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    accounts_payable_id = models.CharField(max_length=255, help_text='QBO Accounts Payable account id', null=True)
    vendor_id = models.CharField(max_length=255, help_text='QBO vendor id')
    department_id = models.CharField(max_length=255, help_text='QBO department id', null=True)
    transaction_date = models.DateField(help_text='Bill transaction date')
    currency = models.CharField(max_length=255, help_text='Bill Currency')
    private_note = models.TextField(help_text='Bill Description')
    payment_synced = models.BooleanField(help_text='Payment synced status', default=False)
    paid_on_qbo = models.BooleanField(help_text='Payment status in QBO', default=False)
    is_retired = models.BooleanField(help_text='Is Payment sync retried', default=False)
    exchange_rate = models.FloatField(help_text='Exchange rate', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')
    bill_number = models.CharField(max_length=255, help_text='Bill Number', null=True)

    class Meta:
        db_table = 'bills'

    @staticmethod
    def create_bill(expense_group: ExpenseGroup, system_comments: list = None):
        """
        Create bill
        :param expense_group: expense group
        :param system_comments: Optional list to collect system comment data
        :return: bill object
        """
        description = expense_group.description

        expense = expense_group.expenses.first()

        department_id = get_department_id_or_none(expense_group)

        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)

        vendor_id = None
        if expense_group.fund_source == 'PERSONAL':
            vendor_id = EmployeeMapping.objects.get(source_employee__value=description.get('employee_email'), workspace_id=expense_group.workspace_id).destination_vendor.destination_id
        elif expense_group.fund_source == 'CCC':
            vendor_id = general_mappings.default_ccc_vendor_id
            add_system_comment(
                system_comments=system_comments,
                source=SystemCommentSourceEnum.CREATE_BILL,
                intent=SystemCommentIntentEnum.DEFAULT_VALUE_APPLIED,
                entity_type=SystemCommentEntityTypeEnum.EXPENSE_GROUP,
                workspace_id=expense_group.workspace_id,
                entity_id=expense_group.id,
                reason=SystemCommentReasonEnum.DEFAULT_CCC_VENDOR_APPLIED,
                info={'default_ccc_vendor_id': general_mappings.default_ccc_vendor_id, 'default_ccc_vendor_name': general_mappings.default_ccc_vendor_name},
                persist_without_export=False
            )

        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)

        private_note = construct_private_note(expense_group)

        bill_object, _ = Bill.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'accounts_payable_id': general_mappings.accounts_payable_id,
                'vendor_id': vendor_id,
                'department_id': department_id,
                'transaction_date': get_transaction_date(expense_group),
                'private_note': private_note,
                'currency': expense.currency,
                'bill_number': get_bill_number(expense_group),
            },
        )
        return bill_object


class BillLineitem(models.Model):
    """
    QBO Bill Lineitem
    """

    id = models.AutoField(primary_key=True)
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, help_text='Reference to bill')
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    account_id = models.CharField(max_length=255, help_text='QBO account id', null=True)
    class_id = models.CharField(max_length=255, help_text='QBO class id', null=True)
    customer_id = models.CharField(max_length=255, help_text='QBO customer id', null=True)
    amount = models.FloatField(help_text='Bill amount')
    tax_amount = models.FloatField(null=True, help_text='Tax amount')
    tax_code = models.CharField(max_length=255, help_text='Tax Group ID', null=True)
    billable = models.BooleanField(null=True, help_text='Expense Billable or not')
    description = models.TextField(help_text='QBO bill lineitem description', null=True)
    detail_type = models.CharField(max_length=255, help_text='Detail type for the lineitem', default='AccountBasedExpenseLineDetail')
    item_id = models.CharField(max_length=255, help_text='QBO item id', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'bill_lineitems'

    @staticmethod
    def create_bill_lineitems(expense_group: ExpenseGroup, workspace_general_settings: WorkspaceGeneralSettings, system_comments: list = None):
        """
        Create bill lineitems
        :param expense_group: expense group
        :param workspace_general_settings: Workspace General Settings
        :param system_comments: Optional list to collect system comment data
        :return: lineitems objects
        """
        expenses = expense_group.expenses.all()
        bill = Bill.objects.get(expense_group=expense_group)

        bill_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if (lineitem.category == lineitem.sub_category or lineitem.sub_category == None) else '{0} / {1}'.format(lineitem.category, lineitem.sub_category)

            account, detail_type = get_category_mapping_and_detail_type(workspace_general_settings, category, expense_group.workspace_id)

            class_id = get_class_id_or_none(expense_group, lineitem)

            customer_id = get_customer_id_or_none(expense_group, lineitem)

            billable = lineitem.billable
            if billable and not customer_id:
                billable = False
                if system_comments is not None:
                    add_system_comment(
                        system_comments=system_comments,
                        source=SystemCommentSourceEnum.CREATE_BILL_LINEITEMS,
                        intent=SystemCommentIntentEnum.BILLABLE_DISABLED,
                        entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                        workspace_id=expense_group.workspace_id,
                        entity_id=lineitem.id,
                        reason=SystemCommentReasonEnum.BILLABLE_SET_TO_FALSE_MISSING_CUSTOMER,
                        info={'original_billable': lineitem.billable, 'customer_id': customer_id},
                        export_type=ExportTypeEnum.BILL,
                        persist_without_export=False
                    )

            bill_lineitem_object, _ = BillLineitem.objects.update_or_create(
                bill=bill,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.destination.destination_id if detail_type == 'AccountBasedExpenseLineDetail' else None,
                    'class_id': class_id,
                    'customer_id': customer_id,
                    'amount': lineitem.amount,
                    'tax_code': get_tax_code_id_or_none(expense_group, lineitem),
                    'tax_amount': lineitem.tax_amount,
                    'billable': lineitem.billable,
                    'detail_type': detail_type,
                    'item_id': account.destination.destination_id if detail_type == 'ItemBasedExpenseLineDetail' else None,
                    'description': get_expense_purpose(expense_group.workspace_id, lineitem, category, workspace_general_settings),
                },
            )

            bill_lineitem_objects.append(bill_lineitem_object)

        return bill_lineitem_objects


class Cheque(models.Model):
    """
    QBO Cheque
    """

    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    bank_account_id = models.CharField(max_length=255, help_text='QBO Bank account id')
    entity_id = models.CharField(max_length=255, help_text='QBO entity id')
    department_id = models.CharField(max_length=255, help_text='QBO department id', null=True)
    transaction_date = models.DateField(help_text='Cheque transaction date')
    currency = models.CharField(max_length=255, help_text='Cheque Currency')
    private_note = models.TextField(help_text='Cheque Description')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'cheques'

    @staticmethod
    def create_cheque(expense_group: ExpenseGroup):
        """
        Create Cheque
        :param expense_group: expense group
        :return: Cheque object
        """
        description = expense_group.description

        expense = expense_group.expenses.first()

        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)

        private_note = construct_private_note(expense_group)

        department_id = get_department_id_or_none(expense_group)

        cheque_object, _ = Cheque.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'bank_account_id': general_mappings.bank_account_id,
                'entity_id': EmployeeMapping.objects.get(source_employee__value=description.get('employee_email'), workspace_id=expense_group.workspace_id).destination_employee.destination_id,
                'department_id': department_id,
                'transaction_date': get_transaction_date(expense_group),
                'private_note': private_note,
                'currency': expense.currency,
            },
        )
        return cheque_object


class ChequeLineitem(models.Model):
    """
    QBO Cheque Lineitem
    """

    id = models.AutoField(primary_key=True)
    cheque = models.ForeignKey(Cheque, on_delete=models.PROTECT, help_text='Reference to cheque')
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    account_id = models.CharField(max_length=255, help_text='QBO account id', null=True)
    class_id = models.CharField(max_length=255, help_text='QBO class id', null=True)
    customer_id = models.CharField(max_length=255, help_text='QBO customer id', null=True)
    amount = models.FloatField(help_text='Cheque amount')
    tax_amount = models.FloatField(null=True, help_text='Tax amount')
    tax_code = models.CharField(max_length=255, help_text='Tax Group ID', null=True)
    billable = models.BooleanField(null=True, help_text='Expense Billable or not')
    description = models.TextField(help_text='QBO cheque lineitem description', null=True)
    detail_type = models.CharField(max_length=255, help_text='Detail type for the lineitem', default='AccountBasedExpenseLineDetail')
    item_id = models.CharField(max_length=255, help_text='QBO item id', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'cheque_lineitems'

    @staticmethod
    def create_cheque_lineitems(expense_group: ExpenseGroup, workspace_general_settings: WorkspaceGeneralSettings, system_comments: list = None):
        """
        Create cheque lineitems
        :param expense_group: expense group
        :param workspace_general_settings: Workspace General Settings
        :param system_comments: Optional list to collect system comment data
        :return: lineitems objects
        """
        expenses: List[Expense] = expense_group.expenses.all()
        cheque = Cheque.objects.get(expense_group=expense_group)

        cheque_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if (lineitem.category == lineitem.sub_category or lineitem.sub_category == None) else '{0} / {1}'.format(lineitem.category, lineitem.sub_category)

            account, detail_type = get_category_mapping_and_detail_type(workspace_general_settings, category, expense_group.workspace_id)

            class_id = get_class_id_or_none(expense_group, lineitem)

            customer_id = get_customer_id_or_none(expense_group, lineitem)

            billable = lineitem.billable
            if billable and not customer_id:
                billable = False
                if system_comments is not None:
                    add_system_comment(
                        system_comments=system_comments,
                        source=SystemCommentSourceEnum.CREATE_CHEQUE_LINEITEMS,
                        intent=SystemCommentIntentEnum.BILLABLE_DISABLED,
                        entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                        workspace_id=expense_group.workspace_id,
                        entity_id=lineitem.id,
                        reason=SystemCommentReasonEnum.BILLABLE_SET_TO_FALSE_MISSING_CUSTOMER,
                        info={'original_billable': lineitem.billable, 'customer_id': customer_id},
                        export_type=ExportTypeEnum.CHECK,
                        persist_without_export=False
                    )

            cheque_lineitem_object, _ = ChequeLineitem.objects.update_or_create(
                cheque=cheque,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.destination.destination_id if detail_type == 'AccountBasedExpenseLineDetail' else None,
                    'class_id': class_id,
                    'customer_id': customer_id,
                    'amount': lineitem.amount,
                    'tax_amount': lineitem.tax_amount,
                    'tax_code': get_tax_code_id_or_none(expense_group, lineitem),
                    'billable': lineitem.billable,
                    'detail_type': detail_type,
                    'item_id': account.destination.destination_id if detail_type == 'ItemBasedExpenseLineDetail' else None,
                    'description': get_expense_purpose(expense_group.workspace_id, lineitem, category, workspace_general_settings),
                },
            )

            cheque_lineitem_objects.append(cheque_lineitem_object)

        return cheque_lineitem_objects


class QBOExpense(models.Model):
    """
    QBO Expense
    """

    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    expense_account_id = models.CharField(max_length=255, help_text='QBO account id')
    entity_id = models.CharField(max_length=255, help_text='QBO entity id')
    department_id = models.CharField(max_length=255, help_text='QBO department id', null=True)
    transaction_date = models.DateField(help_text='QBO Expense transaction date')
    currency = models.CharField(max_length=255, help_text='QBO Expense Currency')
    private_note = models.TextField(help_text='QBO Expense Description')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'qbo_expenses'

    @staticmethod
    def create_qbo_expense(expense_group: ExpenseGroup, qbo_connection, system_comments: list = None):
        """
        Create QBO Expense
        :param expense_group: expense group
        :param qbo_connection: QBO Connection object
        :param system_comments: Optional list to collect system comment data
        :return: QBO Expense object
        """
        description = expense_group.description

        expense = expense_group.expenses.first()

        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)

        private_note = construct_private_note(expense_group)

        department_id = get_department_id_or_none(expense_group)

        workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)
        employee_field_mapping = workspace_general_settings.employee_field_mapping

        if expense_group.fund_source == 'PERSONAL':
            account_id = general_mappings.qbo_expense_account_id
        else:
            ccc_account_id = get_ccc_account_id(workspace_general_settings, general_mappings, expense, description, 'DEBIT_CARD_EXPENSE', system_comments=system_comments)
            if ccc_account_id:
                account_id = ccc_account_id
            else:
                account_id = general_mappings.default_debit_card_account_id
        if workspace_general_settings.map_merchant_to_vendor and expense_group.fund_source == 'CCC':
            merchant = expense.vendor if expense.vendor else ''

            entity = DestinationAttribute.objects.filter(value__iexact=merchant, attribute_type='VENDOR', workspace_id=expense_group.workspace_id, active=True).order_by('-updated_at').first()

            if not entity:
                destination_attribute = DestinationAttribute.objects.filter(destination_id=account_id, workspace_id=expense_group.workspace_id).first()
                payee_type = 'Debit Card Misc' if destination_attribute.attribute_type == 'BANK_ACCOUNT' else 'Credit Card Misc'
                # In case credit card account is selected, we need to create credit card misc vendor
                entity_id = DestinationAttribute.objects.filter(value=payee_type, workspace_id=expense_group.workspace_id, attribute_type='VENDOR').first()
                if not entity_id:
                    entity_id = qbo_connection.get_or_create_vendor(payee_type, create=True).destination_id
                else:
                    entity_id = entity_id.destination_id

                reason = SystemCommentReasonEnum.DEBIT_CARD_MISC_VENDOR_APPLIED if payee_type == 'Debit Card Misc' else SystemCommentReasonEnum.CREDIT_CARD_MISC_VENDOR_APPLIED
                add_system_comment(
                    system_comments=system_comments,
                    source=SystemCommentSourceEnum.CREATE_QBO_EXPENSE,
                    intent=SystemCommentIntentEnum.VENDOR_NOT_FOUND,
                    entity_type=SystemCommentEntityTypeEnum.EXPENSE_GROUP,
                    workspace_id=expense_group.workspace_id,
                    entity_id=expense_group.id,
                    reason=reason,
                    info={'merchant': merchant, 'fallback_vendor': payee_type},
                    persist_without_export=False
                )
            else:
                entity_id = entity.destination_id

        else:
            entity = EmployeeMapping.objects.get(source_employee__value=description.get('employee_email'), workspace_id=expense_group.workspace_id)
            entity_id = entity.destination_employee.destination_id if employee_field_mapping == 'EMPLOYEE' else entity.destination_vendor.destination_id

        qbo_expense_object, _ = QBOExpense.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'expense_account_id': account_id,
                'entity_id': entity_id,
                'department_id': department_id,
                'transaction_date': get_transaction_date(expense_group),
                'private_note': private_note,
                'currency': expense.currency,
            },
        )
        return qbo_expense_object


class QBOExpenseLineitem(models.Model):
    """
    QBO Expense Lineitem
    """

    id = models.AutoField(primary_key=True)
    qbo_expense = models.ForeignKey(QBOExpense, on_delete=models.PROTECT, help_text='Reference to QBO Expense')
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Fyle Expense')
    account_id = models.CharField(max_length=255, help_text='QBO account id', null=True)
    class_id = models.CharField(max_length=255, help_text='QBO class id', null=True)
    customer_id = models.CharField(max_length=255, help_text='QBO customer id', null=True)
    amount = models.FloatField(help_text='Expense amount')
    tax_amount = models.FloatField(null=True, help_text='Tax amount')
    tax_code = models.CharField(max_length=255, help_text='Tax Group ID', null=True)
    billable = models.BooleanField(null=True, help_text='Expense Billable or not')
    description = models.TextField(help_text='QBO expense lineitem description', null=True)
    detail_type = models.CharField(max_length=255, help_text='Detail type for the lineitem', default='AccountBasedExpenseLineDetail')
    item_id = models.CharField(max_length=255, help_text='QBO item id', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'qbo_expense_lineitems'

    @staticmethod
    def create_qbo_expense_lineitems(expense_group: ExpenseGroup, workspace_general_settings: WorkspaceGeneralSettings, system_comments: list = None):
        """
        Create QBO Expense lineitems
        :param expense_group: expense group
        :param workspace_general_settings: Workspace General Settings
        :param system_comments: Optional list to collect system comment data
        :return: lineitems objects
        """
        expenses: List[Expense] = expense_group.expenses.all()
        qbo_expense = QBOExpense.objects.get(expense_group=expense_group)

        qbo_expense_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if (lineitem.category == lineitem.sub_category or lineitem.sub_category == None) else '{0} / {1}'.format(lineitem.category, lineitem.sub_category)

            account, detail_type = get_category_mapping_and_detail_type(workspace_general_settings, category, expense_group.workspace_id)

            class_id = get_class_id_or_none(expense_group, lineitem)

            customer_id = get_customer_id_or_none(expense_group, lineitem)

            billable = lineitem.billable
            if billable and not customer_id:
                billable = False
                if system_comments is not None:
                    add_system_comment(
                        system_comments=system_comments,
                        source=SystemCommentSourceEnum.CREATE_QBO_EXPENSE_LINEITEMS,
                        intent=SystemCommentIntentEnum.BILLABLE_DISABLED,
                        entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                        workspace_id=expense_group.workspace_id,
                        entity_id=lineitem.id,
                        reason=SystemCommentReasonEnum.BILLABLE_SET_TO_FALSE_MISSING_CUSTOMER,
                        info={'original_billable': lineitem.billable, 'customer_id': customer_id},
                        export_type=ExportTypeEnum.EXPENSE,
                        persist_without_export=False
                    )

            qbo_expense_lineitem_object, _ = QBOExpenseLineitem.objects.update_or_create(
                qbo_expense=qbo_expense,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.destination.destination_id if detail_type == 'AccountBasedExpenseLineDetail' else None,
                    'class_id': class_id,
                    'customer_id': customer_id,
                    'amount': lineitem.amount,
                    'tax_amount': lineitem.tax_amount,
                    'tax_code': get_tax_code_id_or_none(expense_group, lineitem),
                    'billable': billable,
                    'detail_type': detail_type,
                    'item_id': account.destination.destination_id if detail_type == 'ItemBasedExpenseLineDetail' else None,
                    'description': get_expense_purpose(expense_group.workspace_id, lineitem, category, workspace_general_settings),
                },
            )

            qbo_expense_lineitem_objects.append(qbo_expense_lineitem_object)

        return qbo_expense_lineitem_objects


class CreditCardPurchase(models.Model):
    """
    QBO CreditCardPurchase
    """

    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    ccc_account_id = models.CharField(max_length=255, help_text='QBO CCC account id')
    entity_id = models.CharField(max_length=255, help_text='QBO entity id')
    department_id = models.CharField(max_length=255, help_text='QBO department id', null=True)
    transaction_date = models.DateField(help_text='CreditCardPurchase transaction date')
    currency = models.CharField(max_length=255, help_text='CreditCardPurchase Currency')
    private_note = models.TextField(help_text='CreditCardPurchase Description')
    credit_card_purchase_number = models.CharField(max_length=255)
    exchange_rate = models.FloatField(help_text='Exchange rate', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'credit_card_purchases'

    @staticmethod
    def create_credit_card_purchase(expense_group: ExpenseGroup, map_merchant_to_vendor: bool, system_comments: list = None):
        """
        Create CreditCardPurchase
        :param map_merchant_to_vendor: Map merchant to vendor for credit card purchases
        :param expense_group: expense group
        :param system_comments: Optional list to collect system comment data
        :return: CreditCardPurchase object
        """
        description = expense_group.description
        expense = expense_group.expenses.first()
        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
        workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)
        expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=expense_group.workspace_id)
        employee_field_mapping = workspace_general_settings.employee_field_mapping
        entity_id = None

        department_id = get_department_id_or_none(expense_group)

        private_note = construct_private_note(expense_group)

        if map_merchant_to_vendor:
            merchant = expense.vendor if expense.vendor else ''

            entity = DestinationAttribute.objects.filter(value__iexact=merchant, attribute_type='VENDOR', workspace_id=expense_group.workspace_id, active=True).order_by('-updated_at').first()

            if not entity:
                entity_id = DestinationAttribute.objects.filter(value='Credit Card Misc', workspace_id=expense_group.workspace_id, attribute_type='VENDOR').first().destination_id

                add_system_comment(
                    system_comments=system_comments,
                    source=SystemCommentSourceEnum.CREATE_CREDIT_CARD_PURCHASE,
                    intent=SystemCommentIntentEnum.VENDOR_NOT_FOUND,
                    entity_type=SystemCommentEntityTypeEnum.EXPENSE_GROUP,
                    workspace_id=expense_group.workspace_id,
                    entity_id=expense_group.id,
                    reason=SystemCommentReasonEnum.CREDIT_CARD_MISC_VENDOR_APPLIED,
                    info={'merchant': merchant, 'fallback_vendor': 'Credit Card Misc'},
                    persist_without_export=False
                )
            else:
                entity_id = entity.destination_id

        else:
            entity = EmployeeMapping.objects.get(source_employee__value=description.get('employee_email'), workspace_id=expense_group.workspace_id)
            entity_id = entity.destination_employee.destination_id if employee_field_mapping == 'EMPLOYEE' else entity.destination_vendor.destination_id

        ccc_account_id = get_ccc_account_id(workspace_general_settings, general_mappings, expense, description, system_comments=system_comments)

        credit_card_purchase_object, _ = CreditCardPurchase.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'ccc_account_id': ccc_account_id,
                'department_id': department_id,
                'entity_id': entity_id,
                'transaction_date': get_transaction_date(expense_group),
                'private_note': private_note,
                'currency': expense.currency,
                'credit_card_purchase_number': get_credit_card_purchase_number(
                    expense_group,
                    expense,
                    expense_group_settings
                ),
            },
        )
        return credit_card_purchase_object


class CreditCardPurchaseLineitem(models.Model):
    """
    QBO CreditCardPurchase Lineitem
    """

    id = models.AutoField(primary_key=True)
    credit_card_purchase = models.ForeignKey(CreditCardPurchase, on_delete=models.PROTECT, help_text='Reference to credit card purchase')
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    account_id = models.CharField(max_length=255, help_text='QBO account id', null=True)
    class_id = models.CharField(max_length=255, help_text='QBO class id', null=True)
    customer_id = models.CharField(max_length=255, help_text='QBO customer id', null=True)
    amount = models.FloatField(help_text='credit card purchase amount')
    tax_amount = models.FloatField(null=True, help_text='Tax amount')
    tax_code = models.CharField(max_length=255, help_text='Tax Group ID', null=True)
    billable = models.BooleanField(null=True, help_text='Expense Billable or not')
    description = models.TextField(help_text='QBO credit card purchase lineitem description', null=True)
    detail_type = models.CharField(max_length=255, help_text='Detail type for the lineitem', default='AccountBasedExpenseLineDetail')
    item_id = models.CharField(max_length=255, help_text='QBO item id', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'credit_card_purchase_lineitems'

    @staticmethod
    def create_credit_card_purchase_lineitems(expense_group: ExpenseGroup, workspace_general_settings: WorkspaceGeneralSettings, system_comments: list = None):
        """
        Create credit card purchase lineitems
        :param expense_group: expense group
        :param workspace_general_settings: Workspace General Settings
        :param system_comments: Optional list to collect system comment data
        :return: lineitems objects
        """
        expenses: List[Expense] = expense_group.expenses.all()
        credit_card_purchase = CreditCardPurchase.objects.get(expense_group=expense_group)

        credit_card_purchase_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if (lineitem.category == lineitem.sub_category or lineitem.sub_category == None) else '{0} / {1}'.format(lineitem.category, lineitem.sub_category)

            account, detail_type = get_category_mapping_and_detail_type(workspace_general_settings, category, expense_group.workspace_id)

            class_id = get_class_id_or_none(expense_group, lineitem)

            customer_id = get_customer_id_or_none(expense_group, lineitem)

            billable = lineitem.billable
            if billable and not customer_id:
                billable = False
                if system_comments is not None:
                    add_system_comment(
                        system_comments=system_comments,
                        source=SystemCommentSourceEnum.CREATE_CREDIT_CARD_PURCHASE_LINEITEMS,
                        intent=SystemCommentIntentEnum.BILLABLE_DISABLED,
                        entity_type=SystemCommentEntityTypeEnum.EXPENSE,
                        workspace_id=expense_group.workspace_id,
                        entity_id=lineitem.id,
                        reason=SystemCommentReasonEnum.BILLABLE_SET_TO_FALSE_MISSING_CUSTOMER,
                        info={'original_billable': lineitem.billable, 'customer_id': customer_id},
                        export_type=ExportTypeEnum.CREDIT_CARD_PURCHASE,
                        persist_without_export=False
                    )

            credit_card_purchase_lineitem_object, _ = CreditCardPurchaseLineitem.objects.update_or_create(
                credit_card_purchase=credit_card_purchase,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.destination.destination_id if detail_type == 'AccountBasedExpenseLineDetail' else None,
                    'class_id': class_id,
                    'customer_id': customer_id,
                    'amount': lineitem.amount,
                    'tax_amount': lineitem.tax_amount,
                    'tax_code': get_tax_code_id_or_none(expense_group, lineitem),
                    'detail_type': detail_type,
                    'item_id': account.destination.destination_id if detail_type == 'ItemBasedExpenseLineDetail' else None,
                    'billable': billable,
                    'description': get_expense_purpose(expense_group.workspace_id, lineitem, category, workspace_general_settings),
                },
            )

            credit_card_purchase_lineitem_objects.append(credit_card_purchase_lineitem_object)

        return credit_card_purchase_lineitem_objects


class JournalEntry(models.Model):
    """
    QBO JournalEntry
    """

    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    transaction_date = models.DateField(help_text='JournalEntry transaction date')
    currency = models.CharField(max_length=255, help_text='JournalEntry Currency')
    private_note = models.TextField(help_text='JournalEntry Description')
    exchange_rate = models.FloatField(help_text='Exchange rate', null=True)
    journal_number = models.CharField(max_length=255, help_text='Journal number', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'journal_entries'

    @staticmethod
    def create_journal_entry(expense_group: ExpenseGroup):
        """
        Create JournalEntry
        :param expense_group: expense group
        :return: JournalEntry object
        """
        expense = expense_group.expenses.first()

        private_note = construct_private_note(expense_group)

        journal_entry_object, _ = JournalEntry.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                "transaction_date": get_transaction_date(expense_group),
                "private_note": private_note,
                "currency": expense.currency,
                "journal_number": get_journal_number(expense_group),
            },
        )
        return journal_entry_object


class JournalEntryLineitem(models.Model):
    """
    QBO JournalEntry Lineitem
    """

    id = models.AutoField(primary_key=True)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.PROTECT, help_text='Reference to JournalEntry')
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    debit_account_id = models.CharField(max_length=255, help_text='QBO Debit account id')
    account_id = models.CharField(max_length=255, help_text='QBO account id')
    class_id = models.CharField(max_length=255, help_text='QBO class id', null=True)
    entity_id = models.CharField(max_length=255, help_text='QBO entity id')
    entity_type = models.CharField(max_length=255, help_text='QBO Entity Type ( Vendor / Employee )')
    customer_id = models.CharField(max_length=255, help_text='QBO customer id', null=True)
    department_id = models.CharField(max_length=255, help_text='QBO department id', null=True)
    posting_type = models.CharField(max_length=255, help_text='QBO posting type', null=True)
    amount = models.FloatField(help_text='JournalEntry amount')
    tax_amount = models.FloatField(null=True, help_text='Tax amount')
    tax_code = models.CharField(max_length=255, help_text='Tax Group ID', null=True)
    description = models.TextField(help_text='QBO JournalEntry lineitem description', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'journal_entry_lineitems'

    @staticmethod
    def create_journal_entry_lineitems(expense_group: ExpenseGroup, workspace_general_settings: WorkspaceGeneralSettings, entity_map: Dict):
        """
        Create journal_entry lineitems
        :param expense_group: expense group
        :param workspace_general_settings: Workspace General Settings
        :return: lineitems objects
        """
        expenses = expense_group.expenses.all()
        qbo_journal_entry = JournalEntry.objects.get(expense_group=expense_group)

        description = expense_group.description

        debit_account_id = None
        entity_type = None

        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
        workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)
        employee_field_mapping = workspace_general_settings.employee_field_mapping

        debit_account_id = None

        if employee_field_mapping == 'EMPLOYEE':
            entity_type = 'Employee'
        elif employee_field_mapping == 'VENDOR':
            entity_type = 'Vendor'

        journal_entry_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if (lineitem.category == lineitem.sub_category or lineitem.sub_category == None) else '{0} / {1}'.format(lineitem.category, lineitem.sub_category)

            if expense_group.fund_source == 'PERSONAL':
                if employee_field_mapping == 'VENDOR':
                    debit_account_id = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id).accounts_payable_id
                elif employee_field_mapping == 'EMPLOYEE':
                    debit_account_id = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id).bank_account_id
            elif expense_group.fund_source == 'CCC':
                debit_account_id = get_ccc_account_id(workspace_general_settings, general_mappings, lineitem, description)

            account: Mapping = Mapping.objects.filter(source_type='CATEGORY', destination_type='ACCOUNT', source__value=category, workspace_id=expense_group.workspace_id).first()

            class_id = get_class_id_or_none(expense_group, lineitem)

            customer_id = get_customer_id_or_none(expense_group, lineitem)

            department_id = get_department_id_or_none(expense_group, lineitem)

            journal_entry_lineitem_object, _ = JournalEntryLineitem.objects.update_or_create(
                journal_entry=qbo_journal_entry,
                expense_id=lineitem.id,
                defaults={
                    'debit_account_id': debit_account_id,
                    'account_id': account.destination.destination_id if account else None,
                    'class_id': class_id,
                    'entity_id': entity_map[lineitem.id],
                    'entity_type': entity_type,
                    'customer_id': customer_id,
                    'amount': round(lineitem.amount, 2) if workspace_general_settings.je_single_credit_line else lineitem.amount,
                    'tax_amount': round(lineitem.tax_amount, 2) if workspace_general_settings.je_single_credit_line and lineitem.tax_amount else lineitem.tax_amount,
                    'tax_code': get_tax_code_id_or_none(expense_group, lineitem),
                    'department_id': department_id,
                    'description': get_expense_purpose(expense_group.workspace_id, lineitem, category, workspace_general_settings),
                },
            )
            journal_entry_lineitem_objects.append(journal_entry_lineitem_object)
        return journal_entry_lineitem_objects


class BillPayment(models.Model):
    """
    QBO BillPayment
    """

    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    private_note = models.TextField(help_text='Bill Description')
    vendor_id = models.CharField(max_length=255, help_text='QBO vendor id')
    amount = models.FloatField(help_text='Bill amount')
    currency = models.CharField(max_length=255, help_text='Bill Currency')
    payment_account = models.CharField(max_length=255, help_text='Payment Account')
    accounts_payable_id = models.CharField(max_length=255, help_text='QBO Accounts Payable account id', null=True)
    department_id = models.CharField(max_length=255, help_text='QBO department id', null=True)
    transaction_date = models.DateField(help_text='Bill transaction date')
    bill_payment_number = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'bill_payments'

    @staticmethod
    def create_bill_payment(expense_group: ExpenseGroup):
        """
        Create bill payments
        :param expense_group: expense group
        :return: bill payment object
        """
        description = expense_group.description

        expenses: List[Expense] = expense_group.expenses.all()

        total_amount = 0
        for expense in expenses:
            total_amount = total_amount + expense.amount

        expense = expense_group.expenses.first()
        department_id = get_department_id_or_none(expense_group)

        vendor_id = EmployeeMapping.objects.get(source_employee__value=description.get('employee_email'), workspace_id=expense_group.workspace_id).destination_vendor.destination_id

        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
        bill_payment_object, _ = BillPayment.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'private_note': 'Payment for Bill by {0}'.format(description.get('employee_email')),
                'vendor_id': vendor_id,
                'amount': total_amount,
                'currency': expense.currency,
                'payment_account': general_mappings.bill_payment_account_id,
                'accounts_payable_id': general_mappings.accounts_payable_id,
                'department_id': department_id,
                'transaction_date': get_transaction_date(expense_group),
                'bill_payment_number': '',
            },
        )

        return bill_payment_object


class BillPaymentLineitem(models.Model):
    """
    QBO Bill Payment Lineitem
    """

    id = models.AutoField(primary_key=True)
    bill_payment = models.ForeignKey(BillPayment, on_delete=models.PROTECT, help_text='Reference to bill payment')
    amount = models.FloatField(help_text='Bill amount')
    linked_transaction_id = models.CharField(max_length=255, help_text='Linked Transaction ID ( Bill ID )')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'bill_payment_lineitems'

    @staticmethod
    def create_bill_payment_lineitems(expense_group: ExpenseGroup, linked_transaction_id):
        """
        Create bill payment lineitems
        :param linked_transaction_id:
        :param expense_group: expense group
        :return: lineitems objects
        """
        expenses = expense_group.expenses.all()
        bill_payment = BillPayment.objects.get(expense_group=expense_group)

        bill_payment_lineitem_objects = []

        total_amount = 0
        for lineitem in expenses:
            total_amount = total_amount + lineitem.amount
        bill_payment_lineitem_object, _ = BillPaymentLineitem.objects.update_or_create(bill_payment=bill_payment, linked_transaction_id=linked_transaction_id, defaults={'amount': total_amount})
        bill_payment_lineitem_objects.append(bill_payment_lineitem_object)

        return bill_payment_lineitem_objects


class QBOWebhookIncoming(models.Model):
    """
    Table to store webhook data for analysis
    """
    id = models.AutoField(primary_key=True)
    realm_id = models.CharField(
        max_length=40,
        help_text='QBO realm ID',
        db_index=True
    )
    entity_type = models.CharField(
        max_length=50,
        help_text='Entity type (Account, Item, etc.)',
        db_index=True
    )
    destination_id = models.CharField(
        max_length=50,
        help_text='QBO destination ID'
    )
    operation_type = models.CharField(
        max_length=20,
        help_text='Operation type (Create, Update, Delete)',
        db_index=True
    )
    # POC: Storing complete payload for analysis during proof of concept phase
    raw_response = models.JSONField(
        help_text='Complete webhook response'
    )
    last_updated_at = models.DateTimeField(
        help_text='Entity last updated timestamp'
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        help_text='Reference to workspace'
    )
    additional_workspace_ids = models.JSONField(
        default=list,
        help_text='Additional workspace IDs that share the same realm_id'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Webhook received timestamp',
        db_index=True
    )

    class Meta:
        db_table = 'qbo_webhook_incoming'
        indexes = [
            models.Index(fields=['workspace', 'entity_type', 'created_at']),
            models.Index(fields=['realm_id', 'operation_type']),
        ]


class QBOSyncTimestamp(models.Model):
    """
    Table to store sync timestamps
    """
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        help_text='Reference to workspace'
    )
    account_synced_at = models.DateTimeField(help_text='Datetime when accounts were synced last', null=True)
    item_synced_at = models.DateTimeField(help_text='Datetime when items were synced last', null=True)
    vendor_synced_at = models.DateTimeField(help_text='Datetime when vendors were synced last', null=True)
    employee_synced_at = models.DateTimeField(help_text='Datetime when employees were synced last', null=True)
    department_synced_at = models.DateTimeField(help_text='Datetime when departments were synced last', null=True)
    tax_code_synced_at = models.DateTimeField(help_text='Datetime when tax codes were synced last', null=True)
    class_synced_at = models.DateTimeField(help_text='Datetime when classes were synced last', null=True)
    customer_synced_at = models.DateTimeField(help_text='Datetime when customers were synced last', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime', db_index=True)
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime', db_index=True)

    class Meta:
        db_table = 'qbo_sync_timestamps'

    @staticmethod
    def update_sync_timestamp(workspace_id: int, entity_type: str):
        """
        Update sync timestamp
        :param workspace_id: workspace id
        :param entity_type: entity type
        :return: sync timestamp
        """
        qbo_sync_timestamp = QBOSyncTimestamp.objects.get(workspace_id=workspace_id)
        setattr(qbo_sync_timestamp, f'{entity_type}_synced_at', datetime.now())
        qbo_sync_timestamp.save(update_fields=[f'{entity_type}_synced_at', 'updated_at'])


class QBOAttributesCount(models.Model):
    """
    Store QBO attribute counts for each workspace
    """
    id = models.AutoField(primary_key=True)
    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.PROTECT,
        help_text='Reference to workspace',
        related_name='qbo_attributes_count'
    )
    accounts_count = models.IntegerField(default=0, help_text='Number of accounts in QBO')
    items_count = models.IntegerField(default=0, help_text='Number of items in QBO')
    vendors_count = models.IntegerField(default=0, help_text='Number of vendors in QBO')
    employees_count = models.IntegerField(default=0, help_text='Number of employees in QBO')
    departments_count = models.IntegerField(default=0, help_text='Number of departments in QBO')
    classes_count = models.IntegerField(default=0, help_text='Number of classes in QBO')
    customers_count = models.IntegerField(default=0, help_text='Number of customers in QBO')
    tax_codes_count = models.IntegerField(default=0, help_text='Number of tax codes in QBO')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime', db_index=True)

    class Meta:
        db_table = 'qbo_attributes_count'

    @staticmethod
    def update_attribute_count(workspace_id: int, attribute_type: str, count: int):
        """
        Update attribute count for a workspace
        :param workspace_id: Workspace ID
        :param attribute_type: Type of attribute (e.g., 'accounts', 'vendors')
        :param count: Count value from QBO
        """
        qbo_count = QBOAttributesCount.objects.get(workspace_id=workspace_id)
        field_name = f'{attribute_type}_count'
        setattr(qbo_count, field_name, count)
        qbo_count.save(update_fields=[field_name, 'updated_at'])
