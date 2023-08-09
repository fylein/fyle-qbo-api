import json
from datetime import datetime

import pytest
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping

from apps.fyle.models import Expense, ExpenseGroup
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
from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceGeneralSettings


def create_item_based_mapping(workspace_id):
    destination_attribute = DestinationAttribute.objects.create(attribute_type='ACCOUNT', display_name='Item', value='Concrete', destination_id=3, workspace_id=workspace_id, active=True)
    expense_attribute = ExpenseAttribute.objects.create(attribute_type='CATEGORY', display_name='Category', value='Concrete', source_id='253737253737', workspace_id=workspace_id, active=True)
    Mapping.objects.create(source_type='CATEGORY', destination_type='ACCOUNT', destination_id=destination_attribute.id, source_id=expense_attribute.id, workspace_id=workspace_id)


@pytest.fixture
def create_bill(db):

    expense_group = ExpenseGroup.objects.get(id=25)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=4)
    bill = Bill.create_bill(expense_group)
    bill_lineitems = BillLineitem.create_bill_lineitems(expense_group, workspace_general_settings)

    return bill, bill_lineitems


@pytest.fixture
def create_bill_item_and_account_based(db):
    expense_1 = Expense.objects.create(
        employee_email='sravan.kumar@fyle.in',
        employee_name='sravan k',
        category='Concrete',
        project='Bebe Rexha',
        expense_number='E/2023/04/T/2',
        expense_id='txybL0Dw709h',
        org_id='orPJvXuoLqvJ',
        claim_number='C/2023/04/R/2',
        amount=1,
        currency='USD',
        settlement_id='setuFjoPoH1FM',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcwUkHI',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='CCC',
        payment_number='P/2023/04/R/2',
    )

    expense_2 = Expense.objects.create(
        employee_email='sravan.kumar@fyle.in',
        employee_name='sravan k',
        category='WIP',
        project='Bebe Rexha',
        expense_number='E/2023/04/T/3',
        expense_id='txoF0nqv6cG3',
        org_id='orPJvXuoLqvJ',
        claim_number='C/2023/04/R/2',
        amount=10,
        currency='USD',
        settlement_id='setuFjoPoH1FL',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcwUkHI',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='CCC',
        payment_number='P/2023/04/R/3',
    )

    expense_group = ExpenseGroup.objects.create(
        workspace_id=4, fund_source='CCC', description=json.loads('{"report_id": "rpcegBZcwUkHI", "fund_source": "CCC", "claim_number": "C/2023/04/R/2", "employee_email": "sravan.kumar@fyle.in"}'), employee_name='sravan k'
    )

    expense_group.expenses.add(*[expense_1, expense_2])

    create_item_based_mapping(workspace_id=4)

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=4)
    workspace_general_settings.import_items = True
    expense_group = ExpenseGroup.objects.get(id=expense_group.id)
    bill = Bill.create_bill(expense_group)
    bill_lineitems = BillLineitem.create_bill_lineitems(expense_group, workspace_general_settings)

    return bill, bill_lineitems


@pytest.fixture
def create_bill_item_based(db):
    expense = Expense.objects.create(
        employee_email='sravan.kumar@fyle.in',
        employee_name='sravan k',
        category='Concrete',
        expense_id='txT4kpMbHdKn',
        project='Bebe Rexha',
        expense_number='E/2023/04/T/1',
        org_id='orPJvXuoLqvJ',
        claim_number='C/2023/04/R/1',
        amount=1,
        currency='USD',
        settlement_id='setuFjoPoH1FN',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcwUkH',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='CCC',
        payment_number='P/2023/04/R/1',
    )

    expense_group = ExpenseGroup.objects.create(
        workspace_id=4, fund_source='CCC', description=json.loads('{"report_id": "rpcegBZcwUkH", "fund_source": "CCC", "claim_number": "C/2023/04/R/1", "employee_email": "sravan.kumar@fyle.in"}'), employee_name='sravan k'
    )

    expense_group.expenses.add(expense)

    create_item_based_mapping(workspace_id=4)

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=4)
    workspace_general_settings.import_items = True
    expense_group = ExpenseGroup.objects.get(id=expense_group.id)
    bill = Bill.create_bill(expense_group)
    bill_lineitems = BillLineitem.create_bill_lineitems(expense_group, workspace_general_settings)

    return bill, bill_lineitems


@pytest.fixture
def create_credit_card_purchase_item_based(db):
    expense = Expense.objects.create(
        employee_email='sravan.kumar@fyle.in',
        employee_name='sravan k',
        category='Concrete',
        expense_id='txT4kpMbHdLm',
        project='Bebe Rexha',
        expense_number='E/2023/04/T/4',
        org_id='or79Cob97KSh',
        claim_number='C/2023/04/R/3',
        amount=1,
        currency='USD',
        settlement_id='setuFjoPoH1FN',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcwUkH',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='CCC',
        payment_number='P/2023/04/R/4',
    )

    expense_group = ExpenseGroup.objects.create(
        workspace_id=3, fund_source='CCC', description=json.loads('{"report_id": "rpcegBZcwUkH", "fund_source": "CCC", "claim_number": "C/2023/04/R/3", "employee_email": "sravan.kumar@fyle.in"}'), employee_name='sravan k'
    )

    expense_group.expenses.add(expense)

    create_item_based_mapping(workspace_id=3)

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workspace_general_settings.import_items = True
    expense_group = ExpenseGroup.objects.get(id=expense_group.id)
    credit_card_purchase = CreditCardPurchase.create_credit_card_purchase(expense_group, True)
    credit_card_purchase_lineitems = CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(expense_group, workspace_general_settings)

    return credit_card_purchase, credit_card_purchase_lineitems


@pytest.fixture
def create_credit_card_purchase_item_and_account_based(db):
    expense_1 = Expense.objects.create(
        employee_email='sravan.kumar@fyle.in',
        employee_name='sravan k',
        category='Concrete',
        expense_id='txT4kpMbHdLg8',
        project='Bebe Rexha',
        expense_number='E/2023/04/T/6',
        org_id='or79Cob97KSh',
        claim_number='C/2023/04/R/3',
        amount=1,
        currency='USD',
        settlement_id='setuFjoPoH1FN',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcwUkUi',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='CCC',
        payment_number='P/2023/04/R/5',
    )

    expense_2 = Expense.objects.create(
        employee_email='sravan.kumar@fyle.in',
        employee_name='sravan k',
        category='Food',
        project='Bebe Rexha',
        expense_number='E/2023/04/T/7',
        expense_id='txoF0nqv6cG89',
        org_id='or79Cob97KSh',
        claim_number='C/2023/04/R/2',
        amount=10,
        currency='USD',
        settlement_id='setuFjoPoH1FL',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcwUkUiI',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='CCC',
        payment_number='P/2023/04/R/6',
    )

    expense_group = ExpenseGroup.objects.create(
        workspace_id=3, fund_source='CCC', description=json.loads('{"report_id": "rpcegBZcwUkUi", "fund_source": "CCC", "claim_number": "C/2023/04/R/4", "employee_email": "sravan.kumar@fyle.in"}'), employee_name='sravan k'
    )

    expense_group.expenses.add(*[expense_1, expense_2])

    create_item_based_mapping(workspace_id=3)

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workspace_general_settings.import_items = True
    expense_group = ExpenseGroup.objects.get(id=expense_group.id)
    credit_card_purchase = CreditCardPurchase.create_credit_card_purchase(expense_group, True)
    credit_card_purchase_lineitems = CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(expense_group, workspace_general_settings)

    return credit_card_purchase, credit_card_purchase_lineitems


@pytest.fixture
def create_credit_card_purchase(db):

    expense_group = ExpenseGroup.objects.get(id=17)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    credit_card_purchase = CreditCardPurchase.create_credit_card_purchase(expense_group, True)
    credit_card_purchase_lineitems = CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(expense_group, workspace_general_settings)

    return credit_card_purchase, credit_card_purchase_lineitems


@pytest.fixture
def create_journal_entry(db):

    expense_group = ExpenseGroup.objects.get(id=12)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    journal_entry = JournalEntry.create_journal_entry(expense_group)
    entity_ids = []
    expenses = expense_group.expenses.all()
    for x in expenses:
        y = {
            x.id: '173'
        }
        entity_ids.append(y)
    journal_entry_lineitems = JournalEntryLineitem.create_journal_entry_lineitems(expense_group, workspace_general_settings, entity_ids)

    return journal_entry, journal_entry_lineitems


@pytest.fixture
def create_qbo_expense(db):

    expense_group = ExpenseGroup.objects.get(id=14)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    qbo_expense = QBOExpense.create_qbo_expense(expense_group)
    qbo_expense_lineitems = QBOExpenseLineitem.create_qbo_expense_lineitems(expense_group, workspace_general_settings)

    return qbo_expense, qbo_expense_lineitems


@pytest.fixture
def create_qbo_expense_item_based(db):
    expense = Expense.objects.create(
        employee_email='sravan.kumar@fyle.in',
        employee_name='sravan k',
        category='Concrete',
        expense_id='txT4kpMbHdIp',
        project='Bebe Rexha',
        expense_number='E/2023/04/T/10',
        org_id='or79Cob97KSh',
        claim_number='C/2023/04/R/6',
        amount=1,
        currency='USD',
        settlement_id='setuFjoPoH1FN',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcwpoP',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='CCC',
        payment_number='P/2023/04/R/10',
    )

    expense_group = ExpenseGroup.objects.create(
        workspace_id=3, fund_source='CCC', description=json.loads('{"report_id": "rpcegBZcwpoP", "fund_source": "CCC", "claim_number": "C/2023/04/R/6", "employee_email": "sravan.kumar@fyle.in"}'), employee_name='sravan k'
    )

    expense_group.expenses.add(expense)

    create_item_based_mapping(workspace_id=3)

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workspace_general_settings.import_items = True
    expense_group = ExpenseGroup.objects.get(id=expense_group.id)
    qbo_expense = QBOExpense.create_qbo_expense(expense_group)
    qbo_expense_lineitems = QBOExpenseLineitem.create_qbo_expense_lineitems(expense_group, workspace_general_settings)

    return qbo_expense, qbo_expense_lineitems


@pytest.fixture
def create_qbo_expense_item_and_account_based(db):
    expense_1 = Expense.objects.create(
        employee_email='sravan.kumar@fyle.in',
        employee_name='sravan k',
        category='Concrete',
        expense_id='txT4kpMbHdLg87L',
        project='Bebe Rexha',
        expense_number='E/2023/04/T/11',
        org_id='or79Cob97KSh',
        claim_number='C/2023/04/R/6',
        amount=1,
        currency='USD',
        settlement_id='setuFjoPoH1FN',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcwUkpiL',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='CCC',
        payment_number='P/2023/04/R/13',
    )

    expense_2 = Expense.objects.create(
        employee_email='sravan.kumar@fyle.in',
        employee_name='sravan k',
        category='Food',
        project='Bebe Rexha',
        expense_number='E/2023/04/T/12',
        expense_id='txoF0nqv6cG78',
        org_id='or79Cob97KSh',
        claim_number='C/2023/04/R/6',
        amount=10,
        currency='USD',
        settlement_id='setuFjoPoH1FL',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcwUkpiL',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='CCC',
        payment_number='P/2023/04/R/12',
    )

    expense_group = ExpenseGroup.objects.create(
        workspace_id=3, fund_source='CCC', description=json.loads('{"report_id": "rpcegBZcwUkpiL", "fund_source": "CCC", "claim_number": "C/2023/04/R/6", "employee_email": "sravan.kumar@fyle.in"}'), employee_name='sravan k'
    )

    expense_group.expenses.add(*[expense_1, expense_2])

    create_item_based_mapping(workspace_id=3)

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workspace_general_settings.import_items = True
    expense_group = ExpenseGroup.objects.get(id=expense_group.id)
    qbo_expense = QBOExpense.create_qbo_expense(expense_group)
    qbo_expense_lineitems = QBOExpenseLineitem.create_qbo_expense_lineitems(expense_group, workspace_general_settings)

    return qbo_expense, qbo_expense_lineitems


@pytest.fixture
def create_cheque(db):

    expense_group = ExpenseGroup.objects.get(id=12)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    cheque = Cheque.create_cheque(expense_group)
    cheque_lineitems = ChequeLineitem.create_cheque_lineitems(expense_group, workspace_general_settings)

    return cheque, cheque_lineitems


@pytest.fixture
def create_cheque_item_based(db):
    expense = Expense.objects.create(
        employee_email='user9@fyleforgotham.in',
        employee_name='Justin Glass',
        category='Concrete',
        expense_id='txT4kpMbiPlHdLm',
        project='Bebe Rexha',
        expense_number='E/2023/04/T/4',
        org_id='or79Cob97KSh',
        claim_number='C/2023/04/R/7',
        amount=1,
        currency='USD',
        settlement_id='setuFjoPoH1FN',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZciploL',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='PERSONAL',
        payment_number='P/2023/04/R/14',
    )

    expense_group = ExpenseGroup.objects.create(
        workspace_id=3, fund_source='PERSONAL', description=json.loads('{"report_id": "rpcegBZciploL", "fund_source": "PERSONAL", "claim_number": "C/2023/04/R/7", "employee_email": "user9@fyleforgotham.in"}'), employee_name='Justin Glass'
    )

    expense_group.expenses.add(expense)

    create_item_based_mapping(workspace_id=3)

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workspace_general_settings.import_items = True
    expense_group = ExpenseGroup.objects.get(id=expense_group.id)
    cheque = Cheque.create_cheque(expense_group)
    cheque_lineitems = ChequeLineitem.create_cheque_lineitems(expense_group, workspace_general_settings)

    return cheque, cheque_lineitems


@pytest.fixture
def create_cheque_item_and_account_based(db):
    expense_1 = Expense.objects.create(
        employee_email='user9@fyleforgotham.in',
        employee_name='Justin Glass',
        category='Concrete',
        expense_id='txT4kpKidaAdLm',
        project='Bebe Rexha',
        expense_number='E/2023/05/T/4',
        org_id='or79Cob97KSh',
        claim_number='C/2023/04/R/13',
        amount=1,
        currency='USD',
        settlement_id='setuFjoPoH1FN',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcipIpkiLL',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='PERSONAL',
        payment_number='P/2023/04/R/18',
    )

    expense_2 = Expense.objects.create(
        employee_email='user9@fyleforgotham.in',
        employee_name='Justin Glass',
        category='Food',
        expense_id='txT4kpMbiadw',
        project='Bebe Rexha',
        expense_number='E/2023/05/T/4',
        org_id='or79Cob97KSh',
        claim_number='C/2023/04/R/13',
        amount=1,
        currency='USD',
        settlement_id='setuFjoPoH1FN',
        reimbursable=False,
        billable=False,
        state='PAYMENT_PROCESSING',
        vendor=None,
        cost_center='Adidas',
        report_id='rpcegBZcipIpkiLL',
        spent_at=datetime.now(),
        approved_at=datetime.now(),
        expense_created_at=datetime.now(),
        expense_updated_at=datetime.now(),
        custom_properties=json.loads('{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}'),
        fund_source='PERSONAL',
        payment_number='P/2023/04/R/16',
    )

    expense_group = ExpenseGroup.objects.create(
        workspace_id=3, fund_source='PERSONAL', description=json.loads('{"report_id": "rpcegBZcipIpkiLL", "fund_source": "PERSONAL", "claim_number": "C/2023/04/R/13", "employee_email": "user9@fyleforgotham.in"}'), employee_name='Justin Glass'
    )

    expense_group.expenses.add(*[expense_1, expense_2])

    create_item_based_mapping(workspace_id=3)

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workspace_general_settings.import_items = True
    expense_group = ExpenseGroup.objects.get(id=expense_group.id)
    cheque = Cheque.create_cheque(expense_group)
    cheque_lineitems = ChequeLineitem.create_cheque_lineitems(expense_group, workspace_general_settings)

    return cheque, cheque_lineitems


@pytest.fixture
def create_bill_payment(db):

    expense_group = ExpenseGroup.objects.get(id=14)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    bill_payment = BillPayment.create_bill_payment(expense_group)
    bill_payment_lineitems = BillPaymentLineitem.create_bill_payment_lineitems(expense_group, workspace_general_settings)

    return bill_payment, bill_payment_lineitems


@pytest.fixture
def create_task_logs(db):
    TaskLog.objects.update_or_create(workspace_id=3, type='FETCHING_EXPENSES', defaults={'status': 'READY'})

    TaskLog.objects.update_or_create(workspace_id=4, type='FETCHING_EXPENSES', defaults={'status': 'READY'})
