import random
from apps.fyle.models import _format_date, _group_expenses, get_default_ccc_expense_state
from apps.fyle.models import *
from apps.tasks.models import TaskLog
from apps.fyle.tasks import create_expense_groups
from apps.quickbooks_online.tasks import create_bill
from apps.quickbooks_online.models import Bill, get_transaction_date
from fyle_accounting_mappings.models import MappingSetting, Mapping, DestinationAttribute, ExpenseAttribute
from .fixtures import data

def test_default_fields():
    expense_group_field = get_default_expense_group_fields()
    expense_state = get_default_expense_state()
    ccc_expense_state = get_default_ccc_expense_state()

    assert expense_group_field == ['employee_email', 'report_id', 'claim_number', 'fund_source']
    assert expense_state == 'PAYMENT_PROCESSING'
    assert ccc_expense_state == 'PAID'


def test_create_expense_objects(db):
    payload = data['expenses']
    Expense.create_expense_objects(payload, 3)

    expense = Expense.objects.last()
    assert expense.expense_id == 'txLAP0oIB5Yb'


def test_expense_group_settings(create_temp_workspace, db):
    payload = data['expense_group_settings_payload']

    ExpenseGroupSettings.update_expense_group_settings(
        payload, 98
    )

    settings = ExpenseGroupSettings.objects.last()

    assert settings.expense_state == 'PAID'
    assert settings.ccc_export_date_type == 'spent_at'
    assert settings.ccc_expense_state == 'PAID'
 

def test_create_reimbursement(db):

    reimbursements = data['reimbursements']

    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=1)

    pending_reimbursement = Reimbursement.objects.get(reimbursement_id='reimgCW1Og0BcM')

    pending_reimbursement.state = 'PENDING'
    pending_reimbursement.settlement_id= 'setgCxsr2vTmZ'

    reimbursements[0]['is_paid'] = True

    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=1)

    paid_reimbursement = Reimbursement.objects.get(reimbursement_id='reimgCW1Og0BcM')
    paid_reimbursement.state == 'PAID'


def test_create_expense_groups_by_report_id_fund_source(db):
    workspace_id = 4
    payload = data['expenses']
    Expense.create_expense_objects(payload, workspace_id)
    expense_objects = Expense.objects.last()
    
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.reimbursable_export_date_type = 'last_spent_at'
    expense_group_settings.ccc_export_date_type = 'last_spent_at'
    expense_group_settings.save()
    
    field = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').last()
    field.attribute_type = 'KILLUA'
    field.save()

    expenses = Expense.objects.filter(id=33).all()

    expense_groups = _group_expenses(expenses, ['claim_number', 'fund_source', 'project', 'employee_email', 'report_id', 'Killua'], 4)
    assert expense_groups == [{'claim_number': 'C/2022/05/R/6', 'fund_source': 'PERSONAL', 'project': 'Bebe Rexha', 'employee_email': 'sravan.kumar@fyle.in', 'report_id': 'rpawE81idoYo', 'killua': '', 'total': 1, 'expense_ids': [33]}]

    expense_groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source([expense_objects], workspace_id)
    assert len(expense_groups) == 1

    expense_groups = ExpenseGroup.objects.last()
    assert expense_groups.exported_at == None

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    general_settings.reimbursable_expenses_object = 'BILL'
    general_settings.save()

    expenses = expense_groups.expenses.all()
    for expense in expenses:
        if expense.amount > 50:
            expense.amount = -100
        expense.save()

    ExpenseGroup.create_expense_groups_by_report_id_fund_source([expense_objects], workspace_id)

    expense_groups = ExpenseGroup.objects.last()
    assert expense_groups.exported_at == None


def test_format_date():
    date_string = _format_date('2022-05-13T09:32:06.643941Z')

    assert date_string == parser.parse('2022-05-13T09:32:06.643941Z')

def test_support_post_date_integrations(mocker, db, api_client, test_connection):
    workspace_id = 1

    #Import assert

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

    expenses = Expense.objects.filter(id=33).all()

    expense_groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source([expense_objects], workspace_id)
    assert expense_groups[0].description['posted_at'] == '2021-11-08'
    
    mapping_setting = MappingSetting(
        source_field='CATEGORY',
        destination_field='ACCOUNT',
        workspace_id=workspace_id,
        import_to_fyle=False,
        is_custom=False
    )
    mapping_setting.save()

    destination_attribute = DestinationAttribute.objects.create(
        attribute_type='ACCOUNT',
        display_name='Account',
        value='Concreteworks Studio',
        destination_id=321,
        workspace_id=workspace_id,
        active=True,
    )
    destination_attribute.save()
    expense_attribute = ExpenseAttribute.objects.create(
        attribute_type='CATEGORY',
        display_name='Category',
        value='Flight',
        source_id='253737253737',
        workspace_id=workspace_id,
        active=True
    )
    expense_attribute.save()
    mapping = Mapping.objects.create(
        source_type='CATEGORY',
        destination_type='ACCOUNT',
        destination_id=destination_attribute.id,
        source_id=expense_attribute.id,
        workspace_id=workspace_id
    )
    mapping.save()

    mocker.patch(
        'qbosdk.apis.Bills.post',
        return_value={"Bill": {"Id": "sdfghjk"}}
    )

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

    print ('Employee mapping not found', bill.__dict__)
    assert task_log.status == 'COMPLETE'
    assert bill.currency == 'USD'
    assert bill.accounts_payable_id == '33'
    assert bill.vendor_id == '56'
    assert bill.transaction_date.strftime("%m/%d/%Y") == expense_objects.posted_at.strftime("%m/%d/%Y")
