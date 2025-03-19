from apps.fyle.models import ExpenseGroup
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

    export_trigger = ExportSettingsTrigger(workspace_general_settings=workspace_general_settings_payload, workspace_id=workspace_id)
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

    export_trigger = ExportSettingsTrigger(workspace_general_settings=workspace_general_settings_payload, workspace_id=workspace_id)
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

    export_trigger = ExportSettingsTrigger(workspace_general_settings=workspace_general_settings_payload, workspace_id=workspace_id)
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
