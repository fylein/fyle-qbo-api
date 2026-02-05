from datetime import timedelta

from django.utils import timezone as django_timezone

from apps.fyle.models import Expense, ExpenseGroup
from apps.fyle.tasks import (
    handle_category_changes_for_expense,
    delete_expense_group_and_related_data,
)
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.models import (
    Bill,
    BillLineitem,
    Cheque,
    ChequeLineitem,
    QBOExpense,
    QBOExpenseLineitem,
    CreditCardPurchase,
    CreditCardPurchaseLineitem,
    get_ccc_account_id,
)
from apps.quickbooks_online.tasks import validate_for_skipping_payment
from apps.tasks.models import TaskLog
from apps.workspaces.enums import (
    SystemCommentEntityTypeEnum,
    SystemCommentIntentEnum,
    SystemCommentReasonEnum,
    SystemCommentSourceEnum
)
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.workspaces.system_comments import add_system_comment
from fyle_accounting_mappings.models import Mapping, MappingSetting


def test_add_system_comment():
    """
    Test add_system_comment creates correct dict
    """
    system_comments = []

    add_system_comment(
        system_comments=system_comments,
        source=SystemCommentSourceEnum.GET_CCC_ACCOUNT_ID,
        intent=SystemCommentIntentEnum.DEFAULT_VALUE_APPLIED,
        entity_type=SystemCommentEntityTypeEnum.EXPENSE,
        workspace_id=1,
        entity_id=100,
        reason=SystemCommentReasonEnum.DEFAULT_CCC_ACCOUNT_APPLIED,
        info={'default_ccc_account_id': 'acc_123', 'default_ccc_account_name': 'Test Account'}
    )

    assert len(system_comments) == 1
    assert system_comments[0]['workspace_id'] == 1
    assert system_comments[0]['source'] == 'GET_CCC_ACCOUNT_ID'
    assert system_comments[0]['intent'] == 'DEFAULT_VALUE_APPLIED'
    assert system_comments[0]['entity_type'] == 'EXPENSE'
    assert system_comments[0]['entity_id'] == 100
    assert system_comments[0]['detail']['info']['default_ccc_account_id'] == 'acc_123'


def test_category_change_generates_comment(db, add_category_test_expense, add_category_test_expense_group):
    """
    Test handle_category_changes_for_expense generates system comment
    """
    expense = add_category_test_expense
    _ = add_category_test_expense_group
    old_category = expense.category

    system_comments = []

    handle_category_changes_for_expense(
        expense=expense,
        new_category='New Test Category',
        system_comments=system_comments
    )

    assert len(system_comments) >= 1
    comment = system_comments[0]
    assert comment['source'] == 'HANDLE_EXPENSE_CATEGORY_CHANGE'
    assert comment['intent'] == 'UPDATE_EXPENSE_CATEGORY'
    assert comment['entity_type'] == 'EXPENSE'
    assert comment['entity_id'] == expense.id
    assert comment['detail']['reason'] == SystemCommentReasonEnum.CATEGORY_CHANGED.value.format(old=old_category, new='New Test Category')
    assert comment['detail']['info']['old_category'] == old_category
    assert comment['detail']['info']['new_category'] == 'New Test Category'


def test_delete_expense_group_generates_comment(db, create_expense_group_expense):
    """
    Test delete_expense_group_and_related_data generates system comment
    """
    expense_group, _ = create_expense_group_expense

    group_id = expense_group.id
    workspace_id = expense_group.workspace_id

    system_comments = []

    delete_expense_group_and_related_data(
        expense_group=expense_group,
        workspace_id=workspace_id,
        system_comments=system_comments
    )

    assert len(system_comments) >= 1
    comment = system_comments[0]
    assert comment['source'] == 'DELETE_EXPENSE_GROUP_AND_RELATED_DATA'
    assert comment['intent'] == 'DELETE_EXPENSE_GROUP'
    assert comment['entity_type'] == 'EXPENSE_GROUP'
    assert comment['entity_id'] == group_id
    assert comment['detail']['reason'] == SystemCommentReasonEnum.EXPENSE_GROUP_AND_RELATED_DATA_DELETED.value


def test_get_ccc_account_id_generates_comment_for_default_account(db, create_expense_group_expense):
    """
    Test get_ccc_account_id generates system comment when default CCC account is used
    """
    expense_group, expense = create_expense_group_expense
    workspace_id = expense_group.workspace_id

    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()

    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()

    workspace_general_settings.map_fyle_cards_qbo_account = True
    workspace_general_settings.save()

    expense.corporate_card_id = 'card_999'
    expense.save()

    Mapping.objects.filter(
        source_type='CORPORATE_CARD',
        destination_type='CREDIT_CARD_ACCOUNT',
        workspace_id=workspace_id
    ).delete()

    system_comments = []

    result = get_ccc_account_id(
        workspace_general_settings=workspace_general_settings,
        general_mappings=general_mappings,
        expense=expense,
        description=expense_group.description,
        export_type='CREDIT_CARD_EXPENSE',
        system_comments=system_comments
    )

    assert result == general_mappings.default_ccc_account_id
    assert len(system_comments) >= 1
    comment = system_comments[0]
    assert comment['source'] == 'GET_CCC_ACCOUNT_ID'
    assert comment['intent'] in ['DEFAULT_VALUE_APPLIED', 'EMPLOYEE_DEFAULT_VALUE_APPLIED']
    assert comment['entity_type'] == 'EXPENSE'
    assert comment['entity_id'] == expense.id


def test_no_comment_when_system_comments_is_none(db):
    """
    Test no error when system_comments parameter is None
    """
    expense_group = ExpenseGroup.objects.filter(workspace_id=3).first()
    expense = expense_group.expenses.first()
    workspace_id = expense_group.workspace_id

    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()

    workspace_general_settings.map_fyle_cards_qbo_account = False
    workspace_general_settings.save()

    get_ccc_account_id(
        workspace_general_settings=workspace_general_settings,
        general_mappings=general_mappings,
        expense=expense,
        description=expense_group.description,
        export_type='CREDIT_CARD_EXPENSE',
        system_comments=None
    )


def test_ccc_account_comment_has_persist_without_export_false(db, create_expense_group_expense):
    """
    Test get_ccc_account_id sets persist_without_export=False for export-time decisions
    """
    expense_group, expense = create_expense_group_expense
    workspace_id = expense_group.workspace_id

    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()

    workspace_general_settings.map_fyle_cards_qbo_account = True
    workspace_general_settings.save()

    expense.corporate_card_id = 'card_persist_test'
    expense.save()

    Mapping.objects.filter(
        source_type='CORPORATE_CARD',
        destination_type='CREDIT_CARD_ACCOUNT',
        workspace_id=workspace_id
    ).delete()

    system_comments = []

    get_ccc_account_id(
        workspace_general_settings=workspace_general_settings,
        general_mappings=general_mappings,
        expense=expense,
        description=expense_group.description,
        export_type='CREDIT_CARD_EXPENSE',
        system_comments=system_comments
    )

    assert len(system_comments) >= 1
    comment = system_comments[0]
    assert comment['persist_without_export'] is False


def test_validate_for_skipping_payment_generates_system_comment(db):
    """
    Test validate_for_skipping_payment generates system comment when payment is skipped (P1)
    """
    workspace_id = 3
    expense_group = ExpenseGroup.objects.create(workspace_id=workspace_id, fund_source='PERSONAL')

    expense = Expense.objects.create(
        workspace_id=workspace_id,
        expense_id='tx_payment_skip_test',
        employee_email='test@fyle.in',
        category='Test Category',
        amount=100,
        currency='USD',
        org_id='or79Cob97KSh',
        settlement_id='setl_test',
        report_id='rp_test',
        spent_at=django_timezone.now(),
        expense_created_at=django_timezone.now(),
        expense_updated_at=django_timezone.now(),
        fund_source='PERSONAL'
    )
    expense_group.expenses.add(expense)

    bill = Bill.objects.create(
        expense_group=expense_group,
        accounts_payable_id='ap_test',
        vendor_id='vendor_test',
        transaction_date=django_timezone.now().date(),
        currency='USD',
        private_note='test note'
    )

    now = django_timezone.now()
    task_id = f'PAYMENT_{expense_group.id}'
    task_log = TaskLog.objects.create(
        workspace_id=workspace_id,
        type='CREATING_BILL_PAYMENT',
        task_id=task_id,
        expense_group=expense_group,
        status='READY'
    )
    TaskLog.objects.filter(id=task_log.id).update(
        created_at=now - timedelta(days=70),
        updated_at=now - timedelta(days=70)
    )

    system_comments = []
    result = validate_for_skipping_payment(bill=bill, workspace_id=workspace_id, system_comments=system_comments)

    assert result is True
    assert len(system_comments) >= 1

    comment = system_comments[0]
    assert comment['source'] == 'VALIDATE_SKIPPING_PAYMENT'
    assert comment['intent'] == 'PAYMENT_SKIPPED'
    assert comment['entity_type'] == 'EXPENSE'
    assert comment['entity_id'] == expense.id
    assert comment['detail']['reason'] == SystemCommentReasonEnum.PAYMENT_SKIPPED_TASK_LOG_RETIRED.value
    assert comment['detail']['info']['expense_group_id'] == expense_group.id
    assert comment['detail']['info']['bill_id'] == bill.id


def test_bill_lineitem_billable_disabled_generates_comment(db):
    """
    Test BillLineitem.create_bill_lineitems generates system comment when billable is disabled (P2)
    """
    expense_group = ExpenseGroup.objects.get(id=25)
    workspace_id = expense_group.workspace_id

    expense = expense_group.expenses.first()
    expense.billable = True
    expense.save()

    MappingSetting.objects.filter(
        workspace_id=workspace_id,
        destination_field='CUSTOMER'
    ).delete()

    Bill.objects.filter(expense_group=expense_group).delete()
    Bill.objects.create(
        expense_group=expense_group,
        accounts_payable_id='ap_test',
        vendor_id='vendor_test',
        transaction_date=django_timezone.now().date(),
        currency='USD',
        private_note='test'
    )

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    system_comments = []
    BillLineitem.create_bill_lineitems(expense_group, workspace_general_settings, system_comments=system_comments)

    billable_comments = [c for c in system_comments if c['intent'] == 'BILLABLE_DISABLED']
    assert len(billable_comments) >= 1

    comment = billable_comments[0]
    assert comment['source'] == 'CREATE_BILL_LINEITEMS'
    assert comment['intent'] == 'BILLABLE_DISABLED'
    assert comment['entity_type'] == 'EXPENSE'
    assert comment['export_type'] == 'BILL'
    assert comment['persist_without_export'] is False
    assert comment['detail']['reason'] == SystemCommentReasonEnum.BILLABLE_SET_TO_FALSE_MISSING_CUSTOMER.value


def test_cheque_lineitem_billable_disabled_generates_comment(db):
    """
    Test ChequeLineitem.create_cheque_lineitems generates system comment when billable is disabled (P2)
    """
    expense_group = ExpenseGroup.objects.get(id=8)
    workspace_id = expense_group.workspace_id

    expense = expense_group.expenses.first()
    expense.billable = True
    expense.save()

    MappingSetting.objects.filter(
        workspace_id=workspace_id,
        destination_field='CUSTOMER'
    ).delete()

    Cheque.objects.filter(expense_group=expense_group).delete()
    Cheque.objects.create(
        expense_group=expense_group,
        bank_account_id='bank_test',
        entity_id='entity_test',
        transaction_date=django_timezone.now().date(),
        currency='USD',
        private_note='test'
    )

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    system_comments = []
    ChequeLineitem.create_cheque_lineitems(expense_group, workspace_general_settings, system_comments=system_comments)

    billable_comments = [c for c in system_comments if c['intent'] == 'BILLABLE_DISABLED']
    assert len(billable_comments) >= 1

    comment = billable_comments[0]
    assert comment['source'] == 'CREATE_CHEQUE_LINEITEMS'
    assert comment['intent'] == 'BILLABLE_DISABLED'
    assert comment['entity_type'] == 'EXPENSE'
    assert comment['export_type'] == 'CHECK'
    assert comment['persist_without_export'] is False


def test_qbo_expense_lineitem_billable_disabled_generates_comment(db):
    """
    Test QBOExpenseLineitem.create_qbo_expense_lineitems generates system comment when billable is disabled (P2)
    """
    workspace_id = 3

    existing_expense = Expense.objects.filter(workspace_id=workspace_id).first()
    category = existing_expense.category if existing_expense else 'Food'

    expense_group = ExpenseGroup.objects.create(workspace_id=workspace_id, fund_source='CCC')

    expense = Expense.objects.create(
        workspace_id=workspace_id,
        expense_id='tx_qbo_expense_billable_test',
        employee_email='test@fyle.in',
        category=category,
        amount=100,
        currency='USD',
        org_id='or79Cob97KSh',
        settlement_id='setl_test',
        report_id='rp_test',
        spent_at=django_timezone.now(),
        expense_created_at=django_timezone.now(),
        expense_updated_at=django_timezone.now(),
        fund_source='CCC',
        billable=True
    )
    expense_group.expenses.add(expense)

    MappingSetting.objects.filter(
        workspace_id=workspace_id,
        destination_field='CUSTOMER'
    ).delete()

    QBOExpense.objects.create(
        expense_group=expense_group,
        expense_account_id='exp_acc_test',
        entity_id='entity_test',
        transaction_date=django_timezone.now().date(),
        currency='USD',
        private_note='test'
    )

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    system_comments = []
    QBOExpenseLineitem.create_qbo_expense_lineitems(expense_group, workspace_general_settings, system_comments=system_comments)

    billable_comments = [c for c in system_comments if c['intent'] == 'BILLABLE_DISABLED']
    assert len(billable_comments) >= 1

    comment = billable_comments[0]
    assert comment['source'] == 'CREATE_QBO_EXPENSE_LINEITEMS'
    assert comment['intent'] == 'BILLABLE_DISABLED'
    assert comment['entity_type'] == 'EXPENSE'
    assert comment['export_type'] == 'EXPENSE'
    assert comment['persist_without_export'] is False


def test_credit_card_purchase_lineitem_billable_disabled_generates_comment(db):
    """
    Test CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems generates system comment when billable is disabled (P2)
    """
    workspace_id = 3

    existing_expense = Expense.objects.filter(workspace_id=workspace_id).first()
    category = existing_expense.category if existing_expense else 'Food'

    expense_group = ExpenseGroup.objects.create(workspace_id=workspace_id, fund_source='CCC')

    expense = Expense.objects.create(
        workspace_id=workspace_id,
        expense_id='tx_ccp_billable_test',
        employee_email='test@fyle.in',
        category=category,
        amount=100,
        currency='USD',
        org_id='or79Cob97KSh',
        settlement_id='setl_test',
        report_id='rp_test',
        spent_at=django_timezone.now(),
        expense_created_at=django_timezone.now(),
        expense_updated_at=django_timezone.now(),
        fund_source='CCC',
        billable=True
    )
    expense_group.expenses.add(expense)

    MappingSetting.objects.filter(
        workspace_id=workspace_id,
        destination_field='CUSTOMER'
    ).delete()

    CreditCardPurchase.objects.create(
        expense_group=expense_group,
        ccc_account_id='ccc_test',
        entity_id='entity_test',
        transaction_date=django_timezone.now().date(),
        currency='USD',
        private_note='test',
        credit_card_purchase_number='CCP001'
    )

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    system_comments = []
    CreditCardPurchaseLineitem.create_credit_card_purchase_lineitems(expense_group, workspace_general_settings, system_comments=system_comments)

    billable_comments = [c for c in system_comments if c['intent'] == 'BILLABLE_DISABLED']
    assert len(billable_comments) >= 1

    comment = billable_comments[0]
    assert comment['source'] == 'CREATE_CREDIT_CARD_PURCHASE_LINEITEMS'
    assert comment['intent'] == 'BILLABLE_DISABLED'
    assert comment['entity_type'] == 'EXPENSE'
    assert comment['export_type'] == 'CREDIT_CARD_PURCHASE'
    assert comment['persist_without_export'] is False
