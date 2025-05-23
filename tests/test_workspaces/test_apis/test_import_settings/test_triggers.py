from datetime import datetime, timezone

from fyle_accounting_mappings.models import MappingSetting

from apps.workspaces.apis.import_settings.triggers import ImportSettingsTrigger
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_integrations_imports.models import ImportLog


def test__reset_import_log_timestamp_case_1(db):
    """
    Case: When the mapping settings is deleted
    """
    workspace_id = 1
    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    import_settings_trigger = ImportSettingsTrigger(
        workspace_general_settings=general_settings,
        mapping_settings=[],
        workspace_id=workspace_id
    )

    current_mapping_settings = MappingSetting.objects.create(
        source_field='PROJECT',
        destination_field='CUSTOMER',
        workspace_id=workspace_id
    )

    ImportLog.objects.create(
        attribute_type='PROJECT',
        status='COMPLETE',
        workspace_id=workspace_id,
        last_successful_run_at=datetime.now(timezone.utc)
    )

    import_settings_trigger._ImportSettingsTrigger__reset_import_log_timestamp(
        current_mapping_settings=[current_mapping_settings],
        new_mappings_settings=[],
        workspace_id=workspace_id
    )

    assert ImportLog.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').first().last_successful_run_at is None


def test__reset_import_log_timestamp_case_2(db):
    """
    Case: When the mapping settings is changed
    """
    workspace_id = 1
    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    import_settings_trigger = ImportSettingsTrigger(
        workspace_general_settings=general_settings,
        mapping_settings=[],
        workspace_id=workspace_id
    )

    current_mapping_settings_dict = [{
        'source_field': 'PROJECT',
        'destination_field': 'CUSTOMER'
    },{
        'source_field': 'COST_CENTER',
        'destination_field': 'DEPARTMENT'
    }]

    new_mapping_settings = [{
        'source_field': 'COST_CENTER',
        'destination_field': 'CUSTOMER'
    },{
        'source_field': 'PROJECT',
        'destination_field': 'DEPARTMENT'
    }]

    for mapping_setting_dict in current_mapping_settings_dict:
        MappingSetting.objects.create(
            source_field=mapping_setting_dict['source_field'],
            destination_field=mapping_setting_dict['destination_field'],
            workspace_id=workspace_id
        )

    current_mapping_settings = MappingSetting.objects.filter(workspace_id=workspace_id)

    ImportLog.objects.create(
        attribute_type='PROJECT',
        status='COMPLETE',
        workspace_id=workspace_id,
        last_successful_run_at=datetime.now(timezone.utc)
    )

    ImportLog.objects.create(
        attribute_type='COST_CENTER',
        status='COMPLETE',
        workspace_id=workspace_id,
        last_successful_run_at=datetime.now(timezone.utc)
    )

    import_settings_trigger._ImportSettingsTrigger__reset_import_log_timestamp(
        current_mapping_settings=current_mapping_settings,
        new_mappings_settings=new_mapping_settings,
        workspace_id=workspace_id
    )

    assert ImportLog.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').first().last_successful_run_at is None
    assert ImportLog.objects.filter(workspace_id=workspace_id, attribute_type='COST_CENTER').first().last_successful_run_at is None
