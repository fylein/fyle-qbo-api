from unittest import mock

from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping

from apps.quickbooks_online.models import QBOSyncTimestamp
from apps.workspaces.models import FyleCredential, QBOCredential
from fyle_integrations_imports.models import ImportLog
from fyle_integrations_imports.tasks import disable_items, trigger_import_via_schedule
from tests.test_fyle_integrations_imports.test_modules.fixtures import projects_data


def test_trigger_import_via_schedule(mocker, db):
    workspace_id = 3
    # delete all the import logs
    ImportLog.objects.filter(workspace_id=workspace_id).delete()
    credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    QBOSyncTimestamp.objects.create(workspace_id=workspace_id)
    with mock.patch('fyle.platform.apis.v1.admin.Projects.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Projects.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Customers.count',
            return_value=41
        )
        mocker.patch(
            'qbosdk.apis.Customers.get_all_generator',
            return_value=[projects_data['create_new_auto_create_projects_destination_attributes']]
        )
        mocker.patch(
            'qbosdk.apis.Customers.get_inactive',
            return_value=[]
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
            destination_sync_methods=['customers'],
            is_auto_sync_enabled=True,
            is_custom= False
        )

        import_logs = ImportLog.objects.filter(workspace_id=workspace_id).first()

        assert import_logs.status == 'COMPLETE'
        assert import_logs.attribute_type == 'PROJECT'


def test_disable_items_1(mocker, db):
    workspace_id = 1

    # Setup: create FyleCredential
    FyleCredential.objects.get(workspace_id=workspace_id)

    # Setup: create DestinationAttribute and ExpenseAttribute to be disabled
    dest_attr = DestinationAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='ACCOUNT',
        display_name='Item',
        value='Test Item',
        destination_id='item-1',
        active=True
    )
    exp_attr = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        value='Test Item',
        source_id='fyle-1',
        active=True
    )
    Mapping.objects.create(
        source_type='CATEGORY',
        destination_type='ACCOUNT',
        source_id=exp_attr.id,
        destination_id=dest_attr.id,
        workspace_id=workspace_id
    )

    # Patch PlatformConnector and its categories.post_bulk
    mock_platform = mocker.patch('fyle_integrations_imports.tasks.PlatformConnector')
    mock_post_bulk = mocker.patch.object(mock_platform.return_value.categories, 'post_bulk')

    # Run
    disable_items(workspace_id=workspace_id, is_import_enabled=False)

    # Assert post_bulk called with correct payload
    mock_post_bulk.assert_called_once_with([{
        'id': 'fyle-1',
        'name': 'Test Item',
        'is_enabled': False
    }])

    # Assert categories.sync called
    mock_platform.return_value.categories.sync.assert_called_once()


def test_disable_items_no_items(mocker, db):
    workspace_id = 1

    # Setup: create FyleCredential
    FyleCredential.objects.get(workspace_id=workspace_id)

    # Patch PlatformConnector and its categories.post_bulk
    mock_platform = mocker.patch('fyle_integrations_imports.tasks.PlatformConnector')
    mock_post_bulk = mocker.patch.object(mock_platform.return_value.categories, 'post_bulk')

    # Run
    disable_items(workspace_id)

    # Assert post_bulk not called (no items to disable)
    mock_post_bulk.assert_not_called()

    # Assert categories.sync called
    mock_platform.return_value.categories.sync.assert_called_once()
