from unittest import mock
from fyle_accounting_mappings.models import (
    DestinationAttribute,
    ExpenseAttribute,
    Mapping,
)
from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import QBOCredential, FyleCredential, Workspace
from fyle_integrations_platform_connector import PlatformConnector
from fyle_integrations_imports.modules.merchants import Merchant
from tests.test_fyle_integrations_imports.test_modules.fixtures import merchants_data


def test_sync_destination_attributes(mocker, db):
    workspace_id = 5

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
        'fyle.platform.apis.v1beta.admin.expense_fields.list_all',
        return_value=[]
    )

    merchant_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert merchant_count == 0

    merchant = Merchant(workspace_id, 'VENDOR', None,  qbo_connection, ['vendors'])
    merchant.sync_expense_attributes(platform)

    merchant_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert merchant_count == 0

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.expense_fields.list_all',
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
    with mock.patch('fyle.platform.apis.v1beta.admin.expense_fields.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Merchants.post',
            return_value=[]
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
    with mock.patch('fyle.platform.apis.v1beta.admin.expense_fields.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Merchants.post',
            return_value=[]
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

    assert fyle_payload == merchants_data['create_fyle_merchants_payload_create_new_case']
