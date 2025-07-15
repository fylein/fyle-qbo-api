from unittest import mock

from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping
from fyle_integrations_platform_connector import PlatformConnector

from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import FyleCredential, QBOCredential, Workspace, WorkspaceGeneralSettings
from fyle_integrations_imports.modules.merchants import Merchant, disable_merchants
from tests.helper import dict_compare_keys
from tests.test_fyle_integrations_imports.test_modules.fixtures import merchants_data


def test_sync_destination_attributes(mocker, db):
    workspace_id = 5

    mocker.patch(
        'qbosdk.apis.Vendors.count',
        return_value=10
    )
    mocker.patch(
        'qbosdk.apis.Vendors.get_inactive',
        return_value=[]
    )
    mocker.patch(
        'qbosdk.apis.Vendors.get_all_generator',
        return_value=[merchants_data['create_new_auto_create_merchants_destination_attributes']]
    )

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').delete()

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count()
    assert destination_attributes_count == 0

    merchant = Merchant(workspace_id, 'VENDOR', None,  qbo_connection, ['vendors'])
    merchant.sync_destination_attributes()

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count()
    assert destination_attributes_count == 2


def test_sync_expense_atrributes(mocker, db):
    workspace_id = 5
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.workspace.fyle_org_id = 'or5qYLrvnoF9'
    fyle_credentials.workspace.save()
    platform = PlatformConnector(fyle_credentials=fyle_credentials)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').delete()

    mocker.patch(
        'fyle.platform.apis.v1.admin.expense_fields.list_all',
        return_value=[]
    )

    merchant_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert merchant_count == 0

    merchant = Merchant(workspace_id, 'VENDOR', None,  qbo_connection, ['vendors'])
    merchant.sync_expense_attributes(platform)

    merchant_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert merchant_count == 0

    mocker.patch(
        'fyle.platform.apis.v1.admin.expense_fields.list_all',
        return_value=merchants_data['create_new_auto_create_merchants_expense_attributes_0']
    )

    merchant = Merchant(workspace_id, 'VENDOR', None,  qbo_connection, ['vendors'])
    merchant.sync_expense_attributes(platform)

    merchant_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert merchant_count == 4


def test_auto_create_destination_attributes(mocker, db):
    workspace_id = 5
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    merchant = Merchant(workspace_id, 'VENDOR', None,  qbo_connection, ['vendors'])
    merchant.sync_after = None

    Workspace.objects.filter(id=workspace_id).update(fyle_org_id='or5qYLrvnoF9')

    # delete all destination attributes, expense attributes and mappings
    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').delete()
    ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').delete()

    mocker.patch(
        'qbosdk.apis.Vendors.get_inactive',
        return_value=[]
    )

    # create new case for merchants import
    with mock.patch('fyle.platform.apis.v1.admin.expense_fields.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Merchants.post',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Vendors.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Vendors.get_all_generator',
            return_value=[merchants_data['create_new_auto_create_merchants_destination_attributes']]
        )
        mock_call.side_effect = [
            merchants_data['create_new_auto_create_merchants_expense_attributes_0'],
            merchants_data['create_new_auto_create_merchants_expense_attributes_1']
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'MERCHANT').count()

        assert expense_attributes_count == 0

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='MERCHANT', destination_type='VENDOR').count()

        assert mappings_count == 0

        merchant.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'MERCHANT').count()

        assert expense_attributes_count == 6

        #  we dont create mappings for merchants
        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='MERCHANT', destination_type='VENDOR').count()

        assert mappings_count == 0

    # create subsequent case for merchants import
    with mock.patch('fyle.platform.apis.v1.admin.expense_fields.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Merchants.post',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Vendors.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Vendors.get_all_generator',
            return_value=[merchants_data['create_new_auto_create_merchants_destination_attributes_subsequent_run']]
        )
        mock_call.side_effect = [
            merchants_data['create_new_auto_create_merchants_expense_attributes_1'],
            merchants_data['create_new_auto_create_merchants_expense_attributes_2']
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'MERCHANT').count()

        assert expense_attributes_count == 6

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='MERCHANT', destination_type='VENDOR').count()

        assert mappings_count == 0

        merchant.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'MERCHANT').count()

        assert expense_attributes_count == 7

        #  we dont create mappings for merchants
        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='MERCHANT', destination_type='VENDOR').count()

        assert mappings_count == 0


def test_construct_fyle_payload(db):
    workspace_id = 5
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    merchant = Merchant(workspace_id, 'VENDOR', None,  qbo_connection, ['vendors'])
    merchant.sync_after = None

    # create new case
    paginated_destination_attributes = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR')
    existing_fyle_attributes_map = {}

    fyle_payload = merchant.construct_fyle_payload(
        paginated_destination_attributes,
        existing_fyle_attributes_map,
    )

    assert dict_compare_keys(fyle_payload, merchants_data['create_fyle_merchants_payload_create_new_case']) == [], 'Payload mismatches'


def test_disable_merchants(db, mocker):
    workspace_id = 5

    merchants_to_disable = {
        'destination_id': {
            'value': 'old_merchant',
            'updated_value': 'new_merchant',
            'code': 'old_merchant_code',
            'updated_code': 'old_merchant_code'
        }
    }

    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='MERCHANT',
        value='old_merchant',
        source_id='source_id',
        active=True
    )

    mock_platform = mocker.patch('fyle_integrations_imports.modules.merchants.PlatformConnector')
    post_call = mocker.patch.object(mock_platform.return_value.merchants, 'post')

    disable_merchants(workspace_id, merchants_to_disable, is_import_to_fyle_enabled=True)

    assert post_call.call_count == 1

    # Test skip if value and updated_value are the same and code is the same (should not call post)
    merchants_to_disable = {
        'destination_id': {
            'value': 'old_merchant_2',
            'updated_value': 'new_merchant',
            'code': 'old_merchant_code',
            'updated_code': 'new_merchant_code'
        }
    }
    disable_merchants(workspace_id, merchants_to_disable, is_import_to_fyle_enabled=True)
    assert post_call.call_count == 1  # No new call

    # Test disable merchant with code in naming
    general_setting = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    general_setting.import_code_fields = ['VENDOR']
    general_setting.save()

    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='MERCHANT',
        value='old_merchant_code: old_merchant',
        source_id='source_id_123',
        active=True
    )

    merchants_to_disable = {
        'destination_id': {
            'value': 'old_merchant',
            'updated_value': 'new_merchant',
            'code': 'old_merchant_code',
            'updated_code': 'old_merchant_code'
        }
    }

    # The payload is just the value list, so we check the return value
    bulk_payload = disable_merchants(workspace_id, merchants_to_disable, is_import_to_fyle_enabled=True)
    assert 'old_merchant_code: old_merchant' in list(bulk_payload)
