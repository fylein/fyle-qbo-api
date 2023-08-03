from datetime import datetime

import pytest
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping, MappingSetting

from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.models import (
    BillPayment,
    BillPaymentLineitem,
    Cheque,
    ChequeLineitem,
    CreditCardPurchase,
    CreditCardPurchaseLineitem,
    JournalEntry,
    JournalEntryLineitem,
    get_ccc_account_id,
    get_class_id_or_none,
    get_customer_id_or_none,
    get_department_id_or_none,
    get_expense_purpose,
    get_tax_code_id_or_none,
    get_transaction_date,
)
from apps.quickbooks_online.tasks import create_bill
from apps.quickbooks_online.utils import Bill, BillLineitem, QBOExpense, QBOExpenseLineitem
from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceGeneralSettings
from tests.test_fyle.fixtures import data
from tests.test_quickbooks_online.fixtures import data as vendor


def test_create_bill(db):

    expense_group = ExpenseGroup.objects.get(id=25)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=4)
    bill = Bill.create_bill(expense_group)
    bill_lineitems = BillLineitem.create_bill_lineitems(expense_group, workspace_general_settings)

    for bill_lineitem in bill_lineitems:
        assert bill_lineitem.amount == 1.0
        assert bill_lineitem.description == 'sravan.kumar@fyle.in - WIP - 2022-05-23 - C/2022/05/R/8 -  - None/app/main/#/enterprise/view_expense/tx3i1mrGprDs?org_id=orPJvXuoLqvJ'
        assert bill_lineitem.billable == None

    assert bill.currency == 'USD'
    assert bill.transaction_date == datetime.now().strftime('%Y-%m-%d')
    assert bill.vendor_id == '84'


def test_qbo_expense(db):

    expense_group = ExpenseGroup.objects.get(id=14)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    qbo_expense = QBOExpense.create_qbo_expense(expense_group)
    qbo_expense_lineitems = QBOExpenseLineitem.create_qbo_expense_lineitems(expense_group, workspace_general_settings)

    for qbo_expense_lineitem in qbo_expense_lineitems:
        assert qbo_expense_lineitem.amount == 1188.0
        assert qbo_expense_lineitem.description == 'user9@fyleforgotham.in - Office Party - 2020-05-13 - C/2021/04/R/42 -  - None/app/main/#/enterprise/view_expense/txU2qpKmrUR9?org_id=or79Cob97KSh'
        assert qbo_expense_lineitem.billable == None

    assert qbo_expense.currency == 'USD'
    assert qbo_expense.transaction_date == datetime.now().strftime('%Y-%m-%d')
    assert qbo_expense.expense_account_id == '35'
    assert qbo_expense.entity_id == '55'

    expense_group = ExpenseGroup.objects.get(id=17)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    qbo_expense = QBOExpense.create_qbo_expense(expense_group)
    qbo_expense_lineitems = QBOExpenseLineitem.create_qbo_expense_lineitems(expense_group, workspace_general_settings)

    for qbo_expense_lineitem in qbo_expense_lineitems:
        assert qbo_expense_lineitem.amount == 1.0
        assert qbo_expense_lineitem.description == 'ashwin.t@fyle.in - Food - 2022-05-17 - C/2022/05/R/5 -  - None/app/main/#/enterprise/view_expense/txj8kWkDTyog?org_id=or79Cob97KSh'
        assert qbo_expense_lineitem.billable == None

    assert qbo_expense.currency == 'USD'
    assert qbo_expense.transaction_date == '2022-05-17'
    assert qbo_expense.expense_account_id == '94'
    assert qbo_expense.entity_id == '60'


def test_create_journal_entry(mocker,db):

    mocker.patch('qbosdk.apis.Vendors.post', return_value=vendor['post_vendor_resp'])
    mocker.patch('qbosdk.apis.Vendors.search_vendor_by_display_name', return_value=None)
    expense_group = ExpenseGroup.objects.get(id=14)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    journal_entry = JournalEntry.create_journal_entry(expense_group)
    journal_entry_lineitems = JournalEntryLineitem.create_journal_entry_lineitems(expense_group, workspace_general_settings)

    for journal_entry_lineitem in journal_entry_lineitems:
        assert journal_entry_lineitem.amount == 1188.0
        assert journal_entry_lineitem.description == 'user9@fyleforgotham.in - Office Party - 2020-05-13 - C/2021/04/R/42 -  - None/app/main/#/enterprise/view_expense/txU2qpKmrUR9?org_id=or79Cob97KSh'

    assert journal_entry.currency == 'USD'
    assert journal_entry.transaction_date == datetime.now().strftime('%Y-%m-%d')

    expense_group = ExpenseGroup.objects.get(id=17)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    journal_entry = JournalEntry.create_journal_entry(expense_group)
    journal_entry_lineitems = JournalEntryLineitem.create_journal_entry_lineitems(expense_group, workspace_general_settings)

    for journal_entry_lineitem in journal_entry_lineitems:
        assert journal_entry_lineitem.amount == 1.0
        assert journal_entry_lineitem.entity_id == '31'
        assert journal_entry_lineitem.description == 'ashwin.t@fyle.in - Food - 2022-05-17 - C/2022/05/R/5 -  - None/app/main/#/enterprise/view_expense/txj8kWkDTyog?org_id=or79Cob97KSh'

    assert journal_entry.currency == 'USD'
    assert journal_entry.transaction_date == '2022-05-17'


def test_create_bill_payment(db):

    expense_group = ExpenseGroup.objects.get(id=17)
    bill = BillPayment.create_bill_payment(expense_group)
    qbo_object_task_log = TaskLog.objects.get(expense_group=bill.expense_group)
    linked_transaction_id = qbo_object_task_log.detail['Purchase']['Id']
    bill_lineitems = BillPaymentLineitem.create_bill_payment_lineitems(expense_group, linked_transaction_id)

    for bill_lineitem in bill_lineitems:
        assert bill_lineitem.amount == 1.0

    assert bill.currency == 'USD'
    assert bill.transaction_date == '2022-05-17'
    assert bill.vendor_id == '31'


def test_create_credit_card_purchase(db):

    expense_group = ExpenseGroup.objects.get(id=17)
    credit_card_purchase = CreditCardPurchase.create_credit_card_purchase(expense_group, True)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    credit_card_purchase_lineitems = CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(expense_group, workspace_general_settings)

    for credit_card_purchase_lineitem in credit_card_purchase_lineitems:
        assert credit_card_purchase_lineitem.amount == 1.0

    assert credit_card_purchase.currency == 'USD'
    assert credit_card_purchase.transaction_date == '2022-05-17'

    credit_card_purchase = CreditCardPurchase.create_credit_card_purchase(expense_group, False)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    credit_card_purchase_lineitems = CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(expense_group, workspace_general_settings)

    for credit_card_purchase_lineitem in credit_card_purchase_lineitems:
        assert credit_card_purchase_lineitem.amount == 1.0

    assert credit_card_purchase.currency == 'USD'
    assert credit_card_purchase.transaction_date == '2022-05-17'


def test_create_cheque(db):

    expense_group = ExpenseGroup.objects.get(id=17)
    cheque = Cheque.create_cheque(expense_group)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    cheque_lineitems = ChequeLineitem.create_cheque_lineitems(expense_group, workspace_general_settings)

    for cheque_lineitem in cheque_lineitems:
        assert cheque_lineitem.amount == 1.0

    assert cheque.currency == 'USD'
    assert cheque.transaction_date == '2022-05-17'


@pytest.mark.django_db(databases=['default'])
def test_get_department_id_or_none(mocker):
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.get_by_id', return_value={'options': ['samp'], 'updated_at': '2020-06-11T13:14:55.201598+00:00'})
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.post', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.sync', return_value=None)
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        location_id = get_department_id_or_none(expense_group, lineitem)
        assert location_id == None

    mapping_setting = MappingSetting.objects.filter(workspace_id=expense_group.workspace_id, destination_field='DEPARTMENT').first()

    mapping_setting.source_field = 'KLASS'
    mapping_setting.save()
    for lineitem in expenses:
        location_id = get_department_id_or_none(expense_group, lineitem)
        assert location_id == None

    mapping_setting.source_field = 'COST_CENTER'
    mapping_setting.save()
    for lineitem in expenses:
        location_id = get_department_id_or_none(expense_group, lineitem)
        assert location_id == None


@pytest.mark.django_db(databases=['default'])
def test_get_tax_code_id_or_none():
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        location_id = get_tax_code_id_or_none(expense_group, lineitem)
        assert location_id == None


@pytest.mark.django_db(databases=['default'])
def test_get_customer_id_or_none():
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        location_id = get_customer_id_or_none(expense_group, lineitem)
        assert location_id == None

    mapping_setting = MappingSetting.objects.filter(workspace_id=expense_group.workspace_id, destination_field='CUSTOMER').first()
    mapping_setting.source_field = 'PROJECT'
    mapping_setting.save()
    for lineitem in expenses:
        location_id = get_customer_id_or_none(expense_group, lineitem)
        assert location_id == None

    mapping_setting.source_field = 'COST_CENTER'
    mapping_setting.save()
    for lineitem in expenses:
        location_id = get_customer_id_or_none(expense_group, lineitem)
        assert location_id == None


@pytest.mark.django_db(databases=['default'])
def test_get_class_id_or_none(mocker):
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.get_by_id', return_value={'options': ['samp'], 'updated_at': '2020-06-11T13:14:55.201598+00:00'})
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.post', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.sync', return_value=None)
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        location_id = get_class_id_or_none(expense_group, lineitem)
        assert location_id == None

    mapping_setting = MappingSetting.objects.filter(workspace_id=expense_group.workspace_id, destination_field='CLASS').first()
    mapping_setting.source_field = 'PROJECT'
    mapping_setting.save()

    for lineitem in expenses:
        location_id = get_class_id_or_none(expense_group, lineitem)
        assert location_id == None

    mapping_setting = MappingSetting.objects.filter(workspace_id=expense_group.workspace_id, destination_field='CLASS').first()
    mapping_setting.source_field = 'KLASS'
    mapping_setting.save()

    for lineitem in expenses:
        location_id = get_class_id_or_none(expense_group, lineitem)
        assert location_id == None


@pytest.mark.django_db(databases=['default'])
def test_get_expense_purpose():

    expense_group = ExpenseGroup.objects.get(id=16)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(lineitem.category, lineitem.sub_category)

        expense_purpose = get_expense_purpose(3, lineitem, category, workspace_general_settings)

        assert expense_purpose == 'ashwin.t@fyle.in - Taxi / None - 2022-05-13 - C/2022/05/R/4 -  - None/app/main/#/enterprise/view_expense/txgUAIXUPQ8r?org_id=or79Cob97KSh'


@pytest.mark.django_db(databases=['default'])
def test_get_transaction_date():

    expense_group = ExpenseGroup.objects.get(id=8)
    transaction_date = get_transaction_date(expense_group)

    assert transaction_date >= datetime.now().strftime('%Y-%m-%d')


@pytest.mark.django_db(databases=['default'])
def test_get_ccc_account_id():

    expense_group = ExpenseGroup.objects.get(id=8)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    expenses = expense_group.expenses.all()
    general_mapping = GeneralMapping.objects.get(workspace_id=3)
    description = expense_group.description

    for lineitem in expenses:
        ccc_account_id = get_ccc_account_id(workspace_general_settings, general_mapping, lineitem, description)
        assert ccc_account_id == '41'

    workspace_general_settings.map_fyle_cards_qbo_account = False
    workspace_general_settings.save()

    for lineitem in expenses:
        ccc_account_id = get_ccc_account_id(workspace_general_settings, general_mapping, lineitem, description)
        assert ccc_account_id == '41'


def test_support_post_date_integrations(mocker, db):
    workspace_id = 1

    # Import assert

    payload = data['expenses']
    expense_id = data['expenses'][0]['id']
    Expense.create_expense_objects(payload, workspace_id)
    expense_objects = Expense.objects.get(expense_id=expense_id)
    expense_objects.reimbursable = False
    expense_objects.fund_source = 'CCC'
    expense_objects.source_account_type = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'
    expense_objects.save()
    assert expense_objects.posted_at.strftime("%m/%d/%Y") == '11/08/2021'

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.corporate_credit_card_expense_group_fields = ['expense_id', 'employee_email', 'project', 'fund_source', 'posted_at']
    expense_group_settings.ccc_export_date_type = 'posted_at'
    expense_group_settings.save()

    field = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').last()
    field.attribute_type = 'KILLUA'
    field.save()

    expense_groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source([expense_objects], workspace_id)
    assert expense_groups[0].description['posted_at'] == '2021-11-08'

    mapping_setting = MappingSetting(source_field='CATEGORY', destination_field='ACCOUNT', workspace_id=workspace_id, import_to_fyle=False, is_custom=False)
    mapping_setting.save()

    destination_attribute = DestinationAttribute.objects.create(attribute_type='ACCOUNT', display_name='Account', value='Concreteworks Studio', destination_id=321, workspace_id=workspace_id, active=True)
    destination_attribute.save()
    expense_attribute = ExpenseAttribute.objects.create(attribute_type='CATEGORY', display_name='Category', value='Flight', source_id='253737253737', workspace_id=workspace_id, active=True)
    expense_attribute.save()
    mapping = Mapping.objects.create(source_type='CATEGORY', destination_type='ACCOUNT', destination_id=destination_attribute.id, source_id=expense_attribute.id, workspace_id=workspace_id)
    mapping.save()

    mocker.patch('qbosdk.apis.Bills.post', return_value={"Bill": {"Id": "sdfghjk"}})

    task_log = TaskLog.objects.first()
    task_log.workspace_id = 1
    task_log.status = 'READY'
    task_log.save()

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=1)

    general_settings.auto_map_employees = 'NAME'
    general_settings.import_items = False
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    create_bill(expense_groups[0], task_log.id, False)

    task_log = TaskLog.objects.get(pk=task_log.id)
    bill = Bill.objects.get(expense_group_id=expense_groups[0].id)

    assert task_log.status == 'COMPLETE'
    assert bill.currency == 'USD'
    assert bill.accounts_payable_id == '33'
    assert bill.vendor_id == '56'
    assert bill.transaction_date.strftime("%m/%d/%Y") == expense_objects.posted_at.strftime("%m/%d/%Y")
