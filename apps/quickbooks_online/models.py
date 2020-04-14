"""
QBO models
"""
from datetime import datetime

from django.db import models

from apps.fyle.models import ExpenseGroup, Expense
from apps.mappings.models import GeneralMapping, EmployeeMapping, CategoryMapping, CostCenterMapping, ProjectMapping
from apps.workspaces.models import WorkspaceGeneralSettings


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
    currency = models.CharField(max_length=5, help_text='Bill Currency')
    private_note = models.TextField(help_text='Bill Description')
    bill_number = models.CharField(max_length=15, unique=True)
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

        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
        bill_object, _ = Bill.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'accounts_payable_id': general_mappings.bank_account_id,
                'vendor_id': EmployeeMapping.objects.get(employee_email=description.get('employee_email')).vendor_id,
                'department_id': None,
                'transaction_date': datetime.now().strftime("%Y-%m-%d"),
                'private_note': 'Report {0} / {1} exported on {2}'.format(
                    expense.claim_number, expense.report_id, datetime.now().strftime("%Y-%m-%d")
                ),
                'bill_number': expense_group.fyle_group_id
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
            account = CategoryMapping.objects.filter(category=lineitem.category,
                                                     sub_category=lineitem.sub_category).first()

            cost_center_mapping = CostCenterMapping.objects.filter(
                cost_center=lineitem.cost_center, workspace_id=expense_group.workspace_id).first()

            project_mapping = ProjectMapping.objects.filter(
                project=lineitem.project, workspace_id=expense_group.workspace_id).first()

            class_id = cost_center_mapping.class_id if cost_center_mapping else None

            customer_id = project_mapping.customer_id if project_mapping else None

            bill_lineitem_object, _ = BillLineitem.objects.update_or_create(
                bill=bill,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.account_id if account else None,
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
    currency = models.CharField(max_length=5, help_text='Cheque Currency')
    private_note = models.TextField(help_text='Cheque Description')
    cheque_number = models.CharField(max_length=55, unique=True)
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
        cheque_object, _ = Cheque.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'bank_account_id': general_mappings.bank_account_id,
                'employee_id': EmployeeMapping.objects.get(
                    employee_email=description.get('employee_email')
                ).employee_id,
                'department_id': None,
                'transaction_date': datetime.now().strftime("%Y-%m-%d"),
                'private_note': 'Report {0} / {1} exported on {2}'.format(
                    expense.claim_number, expense.report_id, datetime.now().strftime("%Y-%m-%d")
                ),
                'cheque_number':  expense_group.fyle_group_id
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
            account = CategoryMapping.objects.filter(category=lineitem.category,
                                                     sub_category=lineitem.sub_category).first()

            cost_center_mapping = CostCenterMapping.objects.filter(
                cost_center=lineitem.cost_center, workspace_id=expense_group.workspace_id).first()

            project_mapping = ProjectMapping.objects.filter(
                project=lineitem.project, workspace_id=expense_group.workspace_id).first()

            class_id = cost_center_mapping.class_id if cost_center_mapping else None

            customer_id = project_mapping.customer_id if project_mapping else None

            cheque_lineitem_object, _ = ChequeLineitem.objects.update_or_create(
                cheque=cheque,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.account_id if account else None,
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
    currency = models.CharField(max_length=5, help_text='CreditCardPurchase Currency')
    private_note = models.TextField(help_text='CreditCardPurchase Description')
    credit_card_purchase_number = models.CharField(max_length=55, unique=True)
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

        general_settings_queryset = WorkspaceGeneralSettings.objects.all()
        general_settings = general_settings_queryset.get(workspace_id=expense_group.workspace_id)

        credit_card_purchase_object, _ = CreditCardPurchase.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'ccc_account_id': EmployeeMapping.objects.get(
                    employee_email=description.get('employee_email')).ccc_account_id,
                'entity_id': EmployeeMapping.objects.get(employee_email=description.get('employee_email')).employee_id
                if general_settings.employee_field_mapping == 'EMPLOYEE' else
                EmployeeMapping.objects.get(employee_email=description.get('employee_email')).vendor_id,
                'transaction_date': datetime.now().strftime("%Y-%m-%d"),
                'private_note': 'Report {0} / {1} exported on {2}'.format(
                    expense.claim_number, expense.report_id, datetime.now().strftime("%Y-%m-%d")
                ),
                'credit_card_purchase_number': expense_group.fyle_group_id
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
            account = CategoryMapping.objects.filter(category=lineitem.category,
                                                     sub_category=lineitem.sub_category).first()

            cost_center_mapping = CostCenterMapping.objects.filter(
                cost_center=lineitem.cost_center, workspace_id=expense_group.workspace_id).first()

            project_mapping = ProjectMapping.objects.filter(
                project=lineitem.project, workspace_id=expense_group.workspace_id).first()

            class_id = cost_center_mapping.class_id if cost_center_mapping else None

            customer_id = project_mapping.customer_id if project_mapping else None

            credit_card_purchase_lineitem_object, _ = CreditCardPurchaseLineitem.objects.update_or_create(
                credit_card_purchase=credit_card_purchase,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.account_id if account else None,
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
    ccc_account_id = models.CharField(max_length=255, help_text='QBO CCC account id')
    transaction_date = models.DateField(help_text='JournalEntry transaction date')
    currency = models.CharField(max_length=5, help_text='JournalEntry Currency')
    private_note = models.TextField(help_text='JournalEntry Description')
    journal_entry_number = models.CharField(max_length=55, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_journal_entry(expense_group: ExpenseGroup):
        """
        Create JournalEntry
        :param expense_group: expense group
        :return: JournalEntry object
        """
        description = expense_group.description

        expense = expense_group.expenses.first()

        general_settings_queryset = WorkspaceGeneralSettings.objects.all()
        general_settings = general_settings_queryset.get(workspace_id=expense_group.workspace_id)

        journal_entry_object, _ = JournalEntry.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'ccc_account_id': GeneralMapping.objects.get().bank_account_id if
                general_settings.reimbursable_expenses_object == 'JOURNAL_ENTRY' else EmployeeMapping.objects.get(
                    employee_email=description.get('employee_email')).ccc_account_id,
                'transaction_date': datetime.now().strftime("%Y-%m-%d"),
                'private_note': 'Report {0} / {1} exported on {2}'.format(
                    expense.claim_number, expense.report_id, datetime.now().strftime("%Y-%m-%d")
                ),
                'journal_entry_number': expense_group.fyle_group_id
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
    account_id = models.CharField(max_length=255, help_text='QBO account id')
    class_id = models.CharField(max_length=255, help_text='QBO class id', null=True)
    entity_id = models.CharField(max_length=255, help_text='QBO entity id')
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

        general_settings_queryset = WorkspaceGeneralSettings.objects.all()
        general_settings = general_settings_queryset.get(workspace_id=expense_group.workspace_id)

        journal_entry_lineitem_objects = []

        for lineitem in expenses:
            account = CategoryMapping.objects.filter(category=lineitem.category,
                                                     sub_category=lineitem.sub_category).first()

            cost_center_mapping = CostCenterMapping.objects.filter(
                cost_center=lineitem.cost_center, workspace_id=expense_group.workspace_id).first()

            project_mapping = ProjectMapping.objects.filter(
                project=lineitem.project, workspace_id=expense_group.workspace_id).first()

            entity_id = EmployeeMapping.objects.get().employee_id\
                if general_settings.employee_field_mapping == 'EMPLOYEE' else EmployeeMapping.objects.get().vendor_id

            class_id = cost_center_mapping.class_id if cost_center_mapping else None

            customer_id = project_mapping.customer_id if project_mapping else None

            journal_entry_lineitem_object, _ = JournalEntryLineitem.objects.update_or_create(
                journal_entry=qbo_journal_entry,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.account_id if account else None,
                    'class_id': class_id,
                    'entity_id': entity_id,
                    'customer_id': customer_id,
                    'amount': lineitem.amount,
                    'description': lineitem.purpose
                }
            )

            journal_entry_lineitem_objects.append(journal_entry_lineitem_object)
        return journal_entry_lineitem_objects
