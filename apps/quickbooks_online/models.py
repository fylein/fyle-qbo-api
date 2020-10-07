"""
QBO models
"""
from datetime import datetime

from django.db import models
from django.db.models import Q

from fyle_accounting_mappings.models import Mapping, MappingSetting, ExpenseAttribute

from apps.fyle.models import ExpenseGroup, Expense, ExpenseGroupSettings
from apps.mappings.models import GeneralMapping


def get_transaction_date(expense_group: ExpenseGroup) -> str:
    if 'spent_at' in expense_group.description and expense_group.description['spent_at']:
        return expense_group.description['spent_at']
    elif 'approved_at' in expense_group.description and expense_group.description['approved_at']:
        return expense_group.description['approved_at']
    elif 'verified_at' in expense_group.description and expense_group.description['verified_at']:
        return expense_group.description['verified_at']

    return datetime.now().strftime("%Y-%m-%d")


def get_class_id_or_none(expense_group: ExpenseGroup, lineitem: Expense):
    class_setting: MappingSetting = MappingSetting.objects.filter(
        workspace_id=expense_group.workspace_id,
        destination_field='CLASS'
    ).first()

    class_id = None

    if class_setting:
        if class_setting.source_field == 'PROJECT':
            source_value = lineitem.project
        elif class_setting.source_field == 'COST_CENTER':
            source_value = lineitem.cost_center
        else:
            attribute = ExpenseAttribute.objects.filter(attribute_type=class_setting.source_field).first()
            source_value = lineitem.custom_properties.get(attribute.display_name, None)

        mapping: Mapping = Mapping.objects.filter(
            source_type=class_setting.source_field,
            destination_type='CLASS',
            source__value=source_value,
            workspace_id=expense_group.workspace_id
        ).first()

        if mapping:
            class_id = mapping.destination.destination_id
    return class_id


def get_customer_id_or_none(expense_group: ExpenseGroup, lineitem: Expense):
    customer_setting: MappingSetting = MappingSetting.objects.filter(
        workspace_id=expense_group.workspace_id,
        destination_field='CUSTOMER'
    ).first()

    customer_id = None

    if customer_setting:
        if customer_setting.source_field == 'PROJECT':
            source_value = lineitem.project
        elif customer_setting.source_field == 'COST_CENTER':
            source_value = lineitem.cost_center
        else:
            attribute = ExpenseAttribute.objects.filter(attribute_type=customer_setting.source_field).first()
            source_value = lineitem.custom_properties.get(attribute.display_name, None)

        mapping: Mapping = Mapping.objects.filter(
            source_type=customer_setting.source_field,
            destination_type='CUSTOMER',
            source__value=source_value,
            workspace_id=expense_group.workspace_id
        ).first()

        if mapping:
            customer_id = mapping.destination.destination_id
    return customer_id


def get_department_id_or_none(expense_group: ExpenseGroup, lineitem: Expense = None):
    department_setting: MappingSetting = MappingSetting.objects.filter(
        workspace_id=expense_group.workspace_id,
        destination_field='DEPARTMENT'
    ).first()

    department_id = None

    if department_setting:
        if lineitem:
            if department_setting.source_field == 'PROJECT':
                source_value = lineitem.project
            elif department_setting.source_field == 'COST_CENTER':
                source_value = lineitem.cost_center
            else:
                attribute = ExpenseAttribute.objects.filter(attribute_type=department_setting.source_field).first()
                source_value = lineitem.custom_properties.get(attribute.display_name, None)
        else:
            source_value = expense_group.description[department_setting.source_field.lower()] if \
                department_setting.source_field.lower() in expense_group.description else None

        mapping: Mapping = Mapping.objects.filter(
            source_type=department_setting.source_field,
            destination_type='DEPARTMENT',
            source__value=source_value,
            workspace_id=expense_group.workspace_id
        ).first()

        if mapping:
            department_id = mapping.destination.destination_id
    return department_id


class Bill(models.Model):
    """
    QBO Bill
    """
    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    accounts_payable_id = models.CharField(max_length=255, help_text='QBO Accounts Payable account id')
    vendor_id = models.CharField(max_length=255, help_text='QBO vendor id')
    department_id = models.CharField(max_length=255, help_text='QBO department id', null=True)
    transaction_date = models.DateField(help_text='Bill transaction date')
    currency = models.CharField(max_length=255, help_text='Bill Currency')
    private_note = models.TextField(help_text='Bill Description')
    bill_number = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_bill(expense_group: ExpenseGroup):
        """
        Create bill
        :param expense_group: expense group
        :return: bill object
        """
        description = expense_group.description

        expense = expense_group.expenses.first()

        department_id = get_department_id_or_none(expense_group)

        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
        bill_object, _ = Bill.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'accounts_payable_id': general_mappings.accounts_payable_id,
                'vendor_id': Mapping.objects.get(
                    source_type='EMPLOYEE',
                    destination_type='VENDOR',
                    source__value=description.get('employee_email'),
                    workspace_id=expense_group.workspace_id
                ).destination.destination_id,
                'department_id': department_id,
                'transaction_date': get_transaction_date(expense_group),
                'private_note': 'Report {0} / {1} exported on {2}'.format(
                    expense.claim_number, expense.report_id, datetime.now().strftime("%Y-%m-%d")
                ),
                'bill_number': ''
            }
        )
        return bill_object


class BillLineitem(models.Model):
    """
    QBO Bill Lineitem
    """
    id = models.AutoField(primary_key=True)
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, help_text='Reference to bill')
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    account_id = models.CharField(max_length=255, help_text='QBO account id')
    class_id = models.CharField(max_length=255, help_text='QBO class id', null=True)
    customer_id = models.CharField(max_length=255, help_text='QBO customer id', null=True)
    amount = models.FloatField(help_text='Bill amount')
    description = models.CharField(max_length=255, help_text='QBO bill lineitem description', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_bill_lineitems(expense_group: ExpenseGroup):
        """
        Create bill lineitems
        :param expense_group: expense group
        :return: lineitems objects
        """
        expenses = expense_group.expenses.all()
        bill = Bill.objects.get(expense_group=expense_group)

        bill_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(
                lineitem.category, lineitem.sub_category)

            account: Mapping = Mapping.objects.filter(
                source_type='CATEGORY',
                destination_type='ACCOUNT',
                source__value=category,
                workspace_id=expense_group.workspace_id
            ).first()

            class_id = get_class_id_or_none(expense_group, lineitem)

            customer_id = get_customer_id_or_none(expense_group, lineitem)

            bill_lineitem_object, _ = BillLineitem.objects.update_or_create(
                bill=bill,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.destination.destination_id if account else None,
                    'class_id': class_id,
                    'customer_id': customer_id,
                    'amount': lineitem.amount,
                    'description': lineitem.purpose
                }
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
    cheque_number = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

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

        department_id = get_department_id_or_none(expense_group)

        cheque_object, _ = Cheque.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'bank_account_id': general_mappings.bank_account_id,
                'entity_id': Mapping.objects.get(
                    source_type='EMPLOYEE',
                    destination_type='EMPLOYEE',
                    source__value=description.get('employee_email'),
                    workspace_id=expense_group.workspace_id
                ).destination.destination_id,
                'department_id': department_id,
                'transaction_date': get_transaction_date(expense_group),
                'private_note': 'Report {0} / {1} exported on {2}'.format(
                    expense.claim_number, expense.report_id, datetime.now().strftime("%Y-%m-%d")
                ),
                'cheque_number': ''
            }
        )
        return cheque_object


class ChequeLineitem(models.Model):
    """
    QBO Cheque Lineitem
    """
    id = models.AutoField(primary_key=True)
    cheque = models.ForeignKey(Cheque, on_delete=models.PROTECT, help_text='Reference to cheque')
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    account_id = models.CharField(max_length=255, help_text='QBO account id')
    class_id = models.CharField(max_length=255, help_text='QBO class id', null=True)
    customer_id = models.CharField(max_length=255, help_text='QBO customer id', null=True)
    amount = models.FloatField(help_text='Cheque amount')
    description = models.CharField(max_length=255, help_text='QBO cheque lineitem description', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_cheque_lineitems(expense_group: ExpenseGroup):
        """
        Create cheque lineitems
        :param expense_group: expense group
        :return: lineitems objects
        """
        expenses = expense_group.expenses.all()
        cheque = Cheque.objects.get(expense_group=expense_group)

        cheque_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(
                lineitem.category, lineitem.sub_category)

            account: Mapping = Mapping.objects.filter(
                source_type='CATEGORY',
                destination_type='ACCOUNT',
                source__value=category,
                workspace_id=expense_group.workspace_id
            ).first()

            class_id = get_class_id_or_none(expense_group, lineitem)

            customer_id = get_customer_id_or_none(expense_group, lineitem)

            cheque_lineitem_object, _ = ChequeLineitem.objects.update_or_create(
                cheque=cheque,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.destination.destination_id if account else None,
                    'class_id': class_id,
                    'customer_id': customer_id,
                    'amount': lineitem.amount,
                    'description': lineitem.purpose
                }
            )

            cheque_lineitem_objects.append(cheque_lineitem_object)

        return cheque_lineitem_objects


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
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_credit_card_purchase(expense_group: ExpenseGroup):
        """
        Create CreditCardPurchase
        :param expense_group: expense group
        :return: CreditCardPurchase object
        """
        description = expense_group.description
        expense = expense_group.expenses.first()

        department_id = get_department_id_or_none(expense_group)

        credit_card_purchase_object, _ = CreditCardPurchase.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'ccc_account_id': Mapping.objects.get(
                    destination_type='CREDIT_CARD_ACCOUNT',
                    source_type='EMPLOYEE',
                    source__value=description.get('employee_email'),
                    workspace_id=expense_group.workspace_id
                ).destination.destination_id,
                'department_id': department_id,
                'entity_id': Mapping.objects.get(
                    Q(destination_type='EMPLOYEE') | Q(destination_type='VENDOR'),
                    source_type='EMPLOYEE',
                    source__value=description.get('employee_email'),
                    workspace_id=expense_group.workspace_id
                ).destination.destination_id,
                'transaction_date': get_transaction_date(expense_group),
                'private_note': 'Report {0} / {1} exported on {2}'.format(
                    expense.claim_number, expense.report_id, datetime.now().strftime("%Y-%m-%d")
                ),
                'credit_card_purchase_number': ''
            }
        )
        return credit_card_purchase_object


class CreditCardPurchaseLineitem(models.Model):
    """
    QBO CreditCardPurchase Lineitem
    """
    id = models.AutoField(primary_key=True)
    credit_card_purchase = models.ForeignKey(CreditCardPurchase, on_delete=models.PROTECT,
                                             help_text='Reference to credit card purchase')
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    account_id = models.CharField(max_length=255, help_text='QBO account id')
    class_id = models.CharField(max_length=255, help_text='QBO class id', null=True)
    customer_id = models.CharField(max_length=255, help_text='QBO customer id', null=True)
    amount = models.FloatField(help_text='credit card purchase amount')
    description = models.CharField(max_length=255, help_text='QBO credit card purchase lineitem description', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_credit_card_purchase_lineitems(expense_group: ExpenseGroup):
        """
        Create credit card purchase lineitems
        :param expense_group: expense group
        :return: lineitems objects
        """
        expenses = expense_group.expenses.all()
        credit_card_purchase = CreditCardPurchase.objects.get(expense_group=expense_group)

        credit_card_purchase_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(
                lineitem.category, lineitem.sub_category)

            account: Mapping = Mapping.objects.filter(
                source_type='CATEGORY',
                destination_type='ACCOUNT',
                source__value=category,
                workspace_id=expense_group.workspace_id
            ).first()

            class_id = get_class_id_or_none(expense_group, lineitem)

            customer_id = get_customer_id_or_none(expense_group, lineitem)

            credit_card_purchase_lineitem_object, _ = CreditCardPurchaseLineitem.objects.update_or_create(
                credit_card_purchase=credit_card_purchase,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.destination.destination_id if account else None,
                    'class_id': class_id,
                    'customer_id': customer_id,
                    'amount': lineitem.amount,
                    'description': lineitem.purpose
                }
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
    journal_entry_number = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_journal_entry(expense_group: ExpenseGroup):
        """
        Create JournalEntry
        :param expense_group: expense group
        :return: JournalEntry object
        """
        expense = expense_group.expenses.first()

        journal_entry_object, _ = JournalEntry.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'transaction_date': get_transaction_date(expense_group),
                'private_note': 'Report {0} / {1} exported on {2}'.format(
                    expense.claim_number, expense.report_id, datetime.now().strftime("%Y-%m-%d")
                ),
                'journal_entry_number': ''
            }
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
    description = models.CharField(max_length=255, help_text='QBO JournalEntry lineitem description', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_journal_entry_lineitems(expense_group: ExpenseGroup):
        """
        Create journal_entry lineitems
        :param expense_group: expense group
        :return: lineitems objects
        """
        expenses = expense_group.expenses.all()
        qbo_journal_entry = JournalEntry.objects.get(expense_group=expense_group)

        description = expense_group.description

        debit_account_id = None
        entity_type = None

        entity = Mapping.objects.get(
            Q(destination_type='EMPLOYEE') | Q(destination_type='VENDOR'),
            source_type='EMPLOYEE',
            source__value=description.get('employee_email'),
            workspace_id=expense_group.workspace_id
        )

        if expense_group.fund_source == 'PERSONAL':
            if entity.destination_type == 'VENDOR':
                debit_account_id = GeneralMapping.objects.get(
                    workspace_id=expense_group.workspace_id).accounts_payable_id
            elif entity.destination_type == 'EMPLOYEE':
                debit_account_id = GeneralMapping.objects.get(
                    workspace_id=expense_group.workspace_id).bank_account_id
        elif expense_group.fund_source == 'CCC':
            debit_account_id = Mapping.objects.get(
                source_type='EMPLOYEE',
                destination_type='CREDIT_CARD_ACCOUNT',
                source__value=description.get('employee_email'),
                workspace_id=expense_group.workspace_id
            ).destination.destination_id

        if entity.destination_type == 'EMPLOYEE':
            entity_type = 'Employee'
        elif entity.destination_type == 'VENDOR':
            entity_type = 'Vendor'

        journal_entry_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(
                lineitem.category, lineitem.sub_category)

            account: Mapping = Mapping.objects.filter(
                source_type='CATEGORY',
                destination_type='ACCOUNT',
                source__value=category,
                workspace_id=expense_group.workspace_id
            ).first()

            class_id = get_class_id_or_none(expense_group, lineitem)

            customer_id = get_customer_id_or_none(expense_group, lineitem)

            department_id = get_department_id_or_none(expense_group)

            journal_entry_lineitem_object, _ = JournalEntryLineitem.objects.update_or_create(
                journal_entry=qbo_journal_entry,
                expense_id=lineitem.id,
                defaults={
                    'debit_account_id': debit_account_id,
                    'account_id': account.destination.destination_id if account else None,
                    'class_id': class_id,
                    'entity_id': entity.destination.destination_id,
                    'entity_type': entity_type,
                    'customer_id': customer_id,
                    'amount': lineitem.amount,
                    'department_id': department_id,
                    'description': lineitem.purpose
                }
            )

            journal_entry_lineitem_objects.append(journal_entry_lineitem_object)
        return journal_entry_lineitem_objects
