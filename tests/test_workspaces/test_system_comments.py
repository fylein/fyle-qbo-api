from apps.fyle.models import ExpenseGroup
from apps.fyle.tasks import (
    handle_category_changes_for_expense,
    delete_expense_group_and_related_data,
)
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.models import get_ccc_account_id
from apps.workspaces.enums import (
    SystemCommentEntityTypeEnum,
    SystemCommentIntentEnum,
    SystemCommentReasonEnum,
    SystemCommentSourceEnum
)
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.workspaces.system_comments import add_system_comment
from fyle_accounting_mappings.models import Mapping


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
