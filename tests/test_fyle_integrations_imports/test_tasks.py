from unittest import mock
from fyle_integrations_imports.tasks import trigger_import_via_schedule
from fyle_integrations_imports.models import ImportLog
from apps.workspaces.models import QBOCredential
from tests.test_fyle_integrations_imports.test_modules.fixtures import projects_data

def test_trigger_import_via_schedule(mocker, db):
    workspace_id = 3
    # delete all the import logs
    ImportLog.objects.filter(workspace_id=workspace_id).delete()
    credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    with mock.patch('fyle.platform.apis.v1beta.admin.Projects.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Projects.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Customers.count',
            return_value=41
        )
        mocker.patch(
            'qbosdk.apis.Customers.get',
            return_value=projects_data['create_new_auto_create_projects_destination_attributes']
        )
        mock_call.side_effect = [
            projects_data['create_new_auto_create_projects_expense_attributes_0'],
            projects_data['create_new_auto_create_projects_expense_attributes_1'] 
        ]

        trigger_import_via_schedule(
            workspace_id=workspace_id,
            destination_field='CUSTOMER',
            source_field='PROJECT',
            sdk_connection_string='apps.quickbooks_online.utils.QBOConnector',
            credentials=credentials,
            destination_sync_method='customers',
            is_auto_sync_enabled=True,
            is_custom= False
        )

        import_logs = ImportLog.objects.filter(workspace_id=workspace_id).first()

        assert import_logs.status == 'COMPLETE'
        assert import_logs.attribute_type == 'PROJECT'
