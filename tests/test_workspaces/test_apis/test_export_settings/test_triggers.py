from fyle_accounting_library.fyle_platform.enums import ExpenseStateEnum

from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.tasks.models import Error, TaskLog
from apps.workspaces.apis.export_settings.triggers import ExportSettingsTrigger
from apps.workspaces.models import WorkspaceGeneralSettings


def test_post_save_workspace_general_settings_export_trigger(mocker, db):
    # setting the import_items to True
    workspace_general_setting = WorkspaceGeneralSettings.objects.filter(workspace_id=5).first()
    workspace_general_setting.import_items = True
    workspace_general_setting.save()

    # payload for the export trigger
    workspace_general_settings_payload = {'reimbursable_expenses_object': 'JOURNAL ENTRY', 'corporate_credit_card_expenses_object': 'JOURNAL ENTRY'}
    workspace_id = 5

    export_trigger = ExportSettingsTrigger(workspace_general_settings=workspace_general_settings_payload, workspace_id=workspace_id, old_configurations={})
    export_trigger.post_save_workspace_general_settings()

    workspace_general_setting = WorkspaceGeneralSettings.objects.filter(workspace_id=5).first()
    assert workspace_general_setting.import_items == False


def test_post_save_workspace_general_settings_export_trigger_2(mocker, db):
    workspace_id = 5
    workspace_general_settings_payload = {
        'reimbursable_expenses_object': 'JOURNAL ENTRY',
        'corporate_credit_card_expenses_object': None
    }

    expense_grp_ccc = ExpenseGroup.objects.filter(
        workspace_id=5,
        exported_at__isnull=True
    ).exclude(fund_source__in=['PERSONAL']).values_list('id', flat=True)

    expense_grp_ccc_count = expense_grp_ccc.count()

    before_delete_count = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status__in=['FAILED', 'FATAL']
    ).count()

    export_trigger = ExportSettingsTrigger(workspace_general_settings=workspace_general_settings_payload, workspace_id=workspace_id, old_configurations={})
    export_trigger.post_save_workspace_general_settings()

    after_delete_count = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status__in=['FAILED', 'FATAL']
    ).count()

    after_errors_count = Error.objects.filter(
        workspace_id=workspace_id,
        expense_group_id__in=expense_grp_ccc
    ).exclude(type__contains='_MAPPING').count()

    assert after_errors_count == 0
    assert after_delete_count == before_delete_count - expense_grp_ccc_count


def test_post_save_workspace_general_settings_export_trigger_3(mocker, db):
    workspace_id = 5
    old_configurations = {
        'reimbursable_expenses_object': 'BILL',
        'corporate_credit_card_expenses_object': 'JOURNAL ENTRY'
    }

    workspace_general_settings_payload = {
        'reimbursable_expenses_object': None,
        'corporate_credit_card_expenses_object': 'JOURNAL ENTRY'
    }

    expense_grp_personal = ExpenseGroup.objects.filter(
        workspace_id=5,
        exported_at__isnull=True
    ).exclude(fund_source__in=['CCC']).values_list('id', flat=True)

    expense_grp_personal_count = expense_grp_personal.count()

    before_delete_count = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status__in=['FAILED', 'FATAL']
    ).count()

    export_trigger = ExportSettingsTrigger(workspace_general_settings=workspace_general_settings_payload, workspace_id=workspace_id, old_configurations=old_configurations)
    export_trigger.post_save_workspace_general_settings()

    after_delete_count = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status__in=['FAILED', 'FATAL']
    ).count()

    after_errors_count = Error.objects.filter(
        workspace_id=workspace_id,
        expense_group_id__in=expense_grp_personal
    ).exclude(type__contains='_MAPPING').count()

    assert after_errors_count == 0
    assert after_delete_count == before_delete_count - expense_grp_personal_count


def test_run_pre_save_expense_group_setting_triggers_no_existing_settings(db, mocker):
    """
    Test when there are no existing expense group settings
    """
    workspace_id = 1
    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).delete()
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)

    workspace_general_settings_payload = {'reimbursable_expenses_object': 'JOURNAL ENTRY', 'corporate_credit_card_expenses_object': 'JOURNAL ENTRY'}

    mock_publish = mocker.patch('apps.workspaces.apis.export_settings.triggers.publish_to_rabbitmq')

    export_trigger = ExportSettingsTrigger(workspace_general_settings=workspace_general_settings_payload, workspace_id=workspace_id, old_configurations={})
    export_trigger.post_save_expense_group_settings(expense_group_settings)
    # Save should not trigger any async tasks since there's no existing settings
    mock_publish.assert_not_called()


def test_run_pre_save_expense_group_setting_triggers_reimbursable_state_change(db, mocker):
    """
    Test when reimbursable expense state changes from PAID to PAYMENT_PROCESSING
    """
    workspace_id = 1

    # Get the existing settings and set it to PAID (old state)
    old_expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    old_expense_group_settings.expense_state = ExpenseStateEnum.PAID
    old_expense_group_settings.save()

    # Create new instance with changed state
    new_expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    new_expense_group_settings.expense_state = ExpenseStateEnum.PAYMENT_PROCESSING

    workspace_general_settings_payload = {'reimbursable_expenses_object': 'JOURNAL ENTRY', 'corporate_credit_card_expenses_object': 'JOURNAL ENTRY'}

    mock_publish = mocker.patch('apps.workspaces.apis.export_settings.triggers.publish_to_rabbitmq')

    export_trigger = ExportSettingsTrigger(
        workspace_general_settings=workspace_general_settings_payload,
        workspace_id=workspace_id,
        old_configurations={'expense_group_settings': old_expense_group_settings}
    )
    export_trigger.post_save_expense_group_settings(new_expense_group_settings)

    assert mock_publish.call_count == 1


def test_run_pre_save_expense_group_setting_triggers_ccc_state_change(db, mocker):
    """
    Test when corporate credit card expense state changes from PAID to APPROVED
    """
    workspace_id = 1

    # Get the existing settings and set it to PAID (old state)
    old_expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    old_expense_group_settings.ccc_expense_state = ExpenseStateEnum.PAID
    old_expense_group_settings.save()

    # Create new instance with changed state
    new_expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    new_expense_group_settings.ccc_expense_state = ExpenseStateEnum.APPROVED

    workspace_general_settings_payload = {'reimbursable_expenses_object': 'JOURNAL ENTRY', 'corporate_credit_card_expenses_object': 'JOURNAL ENTRY'}

    mock_publish = mocker.patch('apps.workspaces.apis.export_settings.triggers.publish_to_rabbitmq')

    export_trigger = ExportSettingsTrigger(
        workspace_general_settings=workspace_general_settings_payload,
        workspace_id=workspace_id,
        old_configurations={'expense_group_settings': old_expense_group_settings}
    )
    export_trigger.post_save_expense_group_settings(new_expense_group_settings)

    assert mock_publish.call_count == 1


def test_run_pre_save_expense_group_setting_triggers_no_configuration(db, mocker):
    """
    Test when workspace general settings don't exist
    """
    workspace_id = 1

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).delete()
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)

    workspace_general_settings_payload = {'reimbursable_expenses_object': 'JOURNAL ENTRY', 'corporate_credit_card_expenses_object': 'JOURNAL ENTRY'}

    mock_publish = mocker.patch('apps.workspaces.apis.export_settings.triggers.publish_to_rabbitmq')

    export_trigger = ExportSettingsTrigger(workspace_general_settings=workspace_general_settings_payload, workspace_id=workspace_id, old_configurations={})
    export_trigger.post_save_expense_group_settings(expense_group_settings)

    # Verify no async tasks were called due to missing configuration
    mock_publish.assert_not_called()


def test_run_pre_save_expense_group_setting_triggers_no_state_change(db, mocker):
    """
    Test when expense states don't change
    """
    workspace_id = 1

    # Get settings with same state for old and new
    old_expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    old_expense_group_settings.expense_state = ExpenseStateEnum.PAID
    old_expense_group_settings.ccc_expense_state = ExpenseStateEnum.PAID
    old_expense_group_settings.save()

    # New instance with same states (no change)
    new_expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    new_expense_group_settings.expense_state = ExpenseStateEnum.PAID
    new_expense_group_settings.ccc_expense_state = ExpenseStateEnum.PAID

    workspace_general_settings_payload = {'reimbursable_expenses_object': 'JOURNAL ENTRY', 'corporate_credit_card_expenses_object': 'JOURNAL ENTRY'}

    mock_publish = mocker.patch('apps.workspaces.apis.export_settings.triggers.publish_to_rabbitmq')

    export_trigger = ExportSettingsTrigger(
        workspace_general_settings=workspace_general_settings_payload,
        workspace_id=workspace_id,
        old_configurations={'expense_group_settings': old_expense_group_settings}
    )
    export_trigger.post_save_expense_group_settings(new_expense_group_settings)

    # Verify no async tasks were called since states didn't change
    mock_publish.assert_not_called()
