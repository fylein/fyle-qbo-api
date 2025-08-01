from unittest import mock

from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping, MappingSetting
from fyle_integrations_platform_connector import PlatformConnector

from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import FyleCredential, QBOCredential, Workspace, WorkspaceGeneralSettings
from fyle_integrations_imports.modules.cost_centers import CostCenter, disable_cost_centers
from tests.helper import dict_compare_keys
from tests.test_fyle_integrations_imports.test_modules.fixtures import cost_center_data


def test_sync_destination_attributes(mocker, db):
    workspace_id = 3

    mocker.patch(
        'qbosdk.apis.Classes.count',
        return_value=10
    )
    mocker.patch(
        'qbosdk.apis.Classes.get_all_generator',
        return_value=[cost_center_data['create_new_auto_create_cost_centers_destination_attributes']]
    )
    mocker.patch(
        'qbosdk.apis.Classes.get_inactive',
        return_value=[]
    )

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='CLASS').count()
    assert destination_attributes_count == 0

    cost_center = CostCenter(workspace_id, 'CLASS', None,  qbo_connection, ['classes'])
    cost_center.sync_destination_attributes()

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='CLASS').count()
    assert destination_attributes_count == 2


def test_sync_expense_atrributes(mocker, db):
    workspace_id = 3
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.workspace.fyle_org_id = 'or5qYLrvnoF9'
    fyle_credentials.workspace.save()
    platform = PlatformConnector(fyle_credentials=fyle_credentials)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch(
        'fyle.platform.apis.v1.admin.CostCenters.list_all',
        return_value=[]
    )

    cost_center_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='COST_CENTER').count()
    assert cost_center_count == 537

    cost_center = CostCenter(workspace_id, 'CLASS', None,  qbo_connection, ['classes'])
    cost_center.sync_expense_attributes(platform)

    cost_center_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='COST_CENTER').count()
    assert cost_center_count == 537

    mocker.patch(
        'fyle.platform.apis.v1.admin.CostCenters.list_all',
        return_value=cost_center_data['create_new_auto_create_cost_centers_expense_attributes_0']
    )
    cost_center.sync_expense_attributes(platform)

    cost_center_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='COST_CENTER').count()
    assert cost_center_count == 543


def test_auto_create_destination_attributes(mocker, db):
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    cost_center = CostCenter(workspace_id, 'CLASS', None,  qbo_connection, ['classes'])
    cost_center.sync_after = None

    Workspace.objects.filter(id=workspace_id).update(fyle_org_id='or5qYLrvnoF9')

    # delete all destination attributes, expense attributes and mappings
    Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER').delete()
    Mapping.objects.filter(workspace_id=workspace_id, destination_type='CLASS').delete()
    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CLASS').delete()
    ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='COST_CENTER').delete()

    # create new case for projects import
    with mock.patch('fyle.platform.apis.v1.admin.CostCenters.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.CostCenters.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Classes.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Classes.get_all_generator',
            return_value=[cost_center_data['create_new_auto_create_cost_centers_destination_attributes']]
        )
        mocker.patch(
            'qbosdk.apis.Classes.get_inactive',
            return_value=[]
        )
        mock_call.side_effect = [
            cost_center_data['create_new_auto_create_cost_centers_expense_attributes_0'],
            cost_center_data['create_new_auto_create_cost_centers_expense_attributes_1']
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'COST_CENTER').count()

        assert expense_attributes_count == 0

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER', destination_type='CLASS').count()

        assert mappings_count == 0

        cost_center.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'COST_CENTER').count()

        assert expense_attributes_count == 8

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER', destination_type='CLASS').count()

        assert mappings_count == 2

    # create new project sub-sequent run (we will be adding 2 new CLASSES)
    with mock.patch('fyle.platform.apis.v1.admin.CostCenters.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.CostCenters.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Classes.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Classes.get_all_generator',
            return_value=[cost_center_data['create_new_auto_create_cost_centers_destination_attributes_subsequent_run']]
        )
        mocker.patch(
            'qbosdk.apis.Classes.get_inactive',
            return_value=[]
        )
        mock_call.side_effect = [
            cost_center_data['create_new_auto_create_cost_centers_expense_attributes_1'],
            cost_center_data['create_new_auto_create_cost_centers_expense_attributes_2']
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'COST_CENTER').count()

        assert expense_attributes_count == 8

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER', destination_type='CLASS').count()

        assert mappings_count == 2

        cost_center.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'COST_CENTER').count()

        assert expense_attributes_count == 10

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER', destination_type='CLASS').count()

        assert mappings_count == 4


def test_construct_fyle_payload(db):
    workspace_id = 5
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    cost_center = CostCenter(workspace_id, 'CLASS', None,  qbo_connection, ['classes'])
    cost_center.sync_after = None

    # create new case
    paginated_destination_attributes = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CLASS')
    existing_fyle_attributes_map = {}

    fyle_payload = cost_center.construct_fyle_payload(
        paginated_destination_attributes,
        existing_fyle_attributes_map,
    )

    assert dict_compare_keys(fyle_payload, cost_center_data['create_fyle_cost_centers_payload_create_new_case']) == [], 'Payload mismatches'


def test_disable_cost_centers(db, mocker):
    workspace_id = 3

    # Setup MappingSetting for destination_type
    MappingSetting.objects.update_or_create(
        workspace_id=workspace_id,
        source_field='COST_CENTER',
        defaults={'destination_field': 'CLASS'}
    )

    cost_centers_to_disable = {
        'destination_id': {
            'value': 'old_cost_center',
            'updated_value': 'new_cost_center',
            'code': 'old_cost_center_code',
            'updated_code': 'old_cost_center_code'
        }
    }

    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='COST_CENTER',
        value='old_cost_center',
        source_id='source_id',
        active=True
    )

    DestinationAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CLASS',
        display_name='Class',
        value='old_cost_center',
        destination_id='old_cost_center_code',
        code='old_cost_center_code'
    )

    mock_platform = mocker.patch('fyle_integrations_imports.modules.cost_centers.PlatformConnector')
    post_bulk_call = mocker.patch.object(mock_platform.return_value.cost_centers, 'post_bulk')

    disable_cost_centers(workspace_id, cost_centers_to_disable, is_import_to_fyle_enabled=True, attribute_type='CLASS')

    assert post_bulk_call.call_count == 1

    # Test skip if value and updated_value are the same and code is the same (should not call post_bulk)
    cost_centers_to_disable = {
        'destination_id': {
            'value': 'old_cost_center_2',
            'updated_value': 'new_cost_center',
            'code': 'old_cost_center_code',
            'updated_code': 'new_cost_center_code'
        }
    }
    disable_cost_centers(workspace_id, cost_centers_to_disable, is_import_to_fyle_enabled=True, attribute_type='CLASS')
    assert post_bulk_call.call_count == 1  # No new call

    # Test disable cost center with code in naming
    general_setting = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    general_setting.import_code_fields = ['CLASS']
    general_setting.save()

    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='COST_CENTER',
        value='old_cost_center_code: old_cost_center',
        source_id='source_id_123',
        active=True
    )

    cost_centers_to_disable = {
        'destination_id': {
            'value': 'old_cost_center',
            'updated_value': 'new_cost_center',
            'code': 'old_cost_center_code',
            'updated_code': 'old_cost_center_code'
        }
    }

    bulk_payload = disable_cost_centers(workspace_id, cost_centers_to_disable, is_import_to_fyle_enabled=True, attribute_type='CLASS')
    # Should contain a dict with name 'old_cost_center_code: old_cost_center'
    assert any(item['name'] == 'old_cost_center_code: old_cost_center' for item in bulk_payload)
