from unittest import mock

from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping

from apps.tasks.models import Error
from apps.workspaces.models import QBOCredential
from fyle_integrations_imports.models import ImportLog
from fyle_integrations_imports.tasks import disable_category_for_items_mapping, trigger_import_via_schedule
from tests.test_fyle_integrations_imports.test_modules.fixtures import categories_data, projects_data


def test_trigger_import_via_schedule(mocker, db):
    workspace_id = 3
    # delete all the import logs
    ImportLog.objects.filter(workspace_id=workspace_id).delete()
    credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
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


def test_disable_category_for_items_mapping(mocker, db):
    workspace_id = 5
    # delete all the import logs
    ImportLog.objects.filter(workspace_id=workspace_id).delete()
    credentials = QBOCredential.get_active_qbo_credentials(workspace_id)

    # case where items mappings is not present
    with mock.patch('fyle.platform.apis.v1.admin.Categories.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Categories.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Items.get',
            return_value=categories_data['create_new_auto_create_categories_destination_attributes_items']
        )
        mocker.patch(
            'qbosdk.apis.Accounts.get',
            return_value=[]
        )
        mock_call.side_effect = [
            categories_data['create_new_auto_create_categories_expense_attributes_1'],
            categories_data['create_new_auto_create_categories_expense_attributes_2']
        ]

        disable_category_for_items_mapping(
            workspace_id,
            'apps.quickbooks_online.utils.QBOConnector',
            credentials
        )

        import_logs = ImportLog.objects.filter(workspace_id=workspace_id).first()

        assert import_logs is None

    # delete all destination attributes, expense attributes and mappings
    Error.objects.filter(workspace_id=workspace_id).delete()
    Mapping.objects.filter(workspace_id=workspace_id, source_type='CATEGORY').delete()
    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT').delete()
    ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').delete()

    # create the item<>category mapping
    destination_attribute = DestinationAttribute.objects.create(
        attribute_type='ACCOUNT',
        display_name='Item',
        value='Machine',
        destination_id='Machine',
        workspace_id=workspace_id,
        active=True
    )

    expense_attribute = ExpenseAttribute.objects.create(
        attribute_type='CATEGORY',
        value='Machine',
        source_id='FyleMachine',
        workspace_id=workspace_id,
        active=True
    )

    Mapping.objects.create(
        source_type='CATEGORY',
        destination_type='ACCOUNT',
        source_id=expense_attribute.id,
        destination_id=destination_attribute.id,
        workspace_id=workspace_id,
    )

    with mock.patch('fyle.platform.apis.v1.admin.Categories.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Categories.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Items.get',
            return_value=categories_data['create_new_auto_create_categories_destination_attributes_items']
        )
        mocker.patch(
            'qbosdk.apis.Accounts.get',
            return_value=[]
        )
        mock_call.side_effect = [
            categories_data['create_new_auto_create_categories_expense_attributes_1'],
            categories_data['create_new_auto_create_categories_expense_attributes_2']
        ]

        disable_category_for_items_mapping(
            workspace_id,
            'apps.quickbooks_online.utils.QBOConnector',
            credentials
        )

        import_logs = ImportLog.objects.filter(workspace_id=workspace_id).first()

        assert import_logs.status in ['COMPLETE', 'IN_PROGRESS']
        assert import_logs.attribute_type == 'CATEGORY'
