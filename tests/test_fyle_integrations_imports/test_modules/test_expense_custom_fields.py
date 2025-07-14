from unittest import mock

from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping
from fyle_integrations_platform_connector import PlatformConnector

from apps.quickbooks_online.models import QBOSyncTimestamp
from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import FyleCredential, QBOCredential, Workspace
from fyle_integrations_imports.modules.expense_custom_fields import ExpenseCustomField
from tests.helper import dict_compare_keys
from tests.test_fyle_integrations_imports.test_modules.fixtures import expense_custom_field_data


def test_sync_expense_atrributes(mocker, db):
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    expense_custom_field = ExpenseCustomField(workspace_id, 'LUKE', 'CLASS', None, qbo_connection, ['classes'])
    expense_custom_field.sync_after = None

    Workspace.objects.filter(id=workspace_id).update(fyle_org_id='or5qYLrvnoF9')
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials=fyle_credentials)

    expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='LUKE').count()
    assert expense_attribute_count == 0

    mocker.patch(
        'fyle.platform.apis.v1.admin.expense_fields.list_all',
        return_value=[]
    )

    expense_custom_field.sync_expense_attributes(platform)

    expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='LUKE').count()
    assert expense_attribute_count == 0

    mocker.patch(
        'fyle.platform.apis.v1.admin.expense_fields.list_all',
        return_value=expense_custom_field_data['create_new_auto_create_expense_custom_fields_expense_attributes_0']
    )

    expense_custom_field.sync_expense_attributes(platform)

    expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='LUKE').count()
    assert expense_attribute_count == 2


def test_auto_create_destination_attributes(mocker, db):
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    QBOSyncTimestamp.objects.create(workspace_id=workspace_id)

    expense_custom_field = ExpenseCustomField(workspace_id, 'LUKE', 'CLASS', None, qbo_connection, ['classes'])
    expense_custom_field.sync_after = None

    Workspace.objects.filter(id=workspace_id).update(fyle_org_id='or5qYLrvnoF9')

    # delete all destination attributes, expense attributes and mappings
    Mapping.objects.filter(workspace_id=workspace_id, source_type='LUKE').delete()
    Mapping.objects.filter(workspace_id=workspace_id, destination_type='CLASS').delete()
    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CLASS').delete()
    ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='LUKE').delete()

    # create new case for projects import
    with mock.patch('fyle.platform.apis.v1.admin.expense_fields.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.ExpenseCustomFields.post',
            return_value=[]
        )

        mocker.patch(
            'fyle_integrations_platform_connector.apis.ExpenseCustomFields.get_by_id',
            return_value=expense_custom_field_data['create_new_auto_create_expense_custom_fields_get_by_id']
        )

        mocker.patch(
            'qbosdk.apis.Classes.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Classes.get_all_generator',
            return_value=[expense_custom_field_data['create_new_auto_create_expense_custom_fields_destination_attributes']]
        )
        mock_call.side_effect = [
            expense_custom_field_data['create_new_auto_create_expense_custom_fields_expense_attributes_0'],
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'LUKE').count()

        assert expense_attributes_count == 0

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='LUKE', destination_type='CLASS').count()

        assert mappings_count == 0

        expense_custom_field.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'LUKE').count()

        assert expense_attributes_count == 2

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='LUKE', destination_type='CLASS').count()

        assert mappings_count == 2

    # create new case for projects import
    with mock.patch('fyle.platform.apis.v1.admin.expense_fields.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.ExpenseCustomFields.post',
            return_value=[]
        )
        mocker.patch(
            'fyle_integrations_platform_connector.apis.ExpenseCustomFields.get_by_id',
            return_value=expense_custom_field_data['create_new_auto_create_expense_custom_fields_get_by_id']
        )
        mocker.patch(
            'qbosdk.apis.Classes.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Classes.get_all_generator',
            return_value=[expense_custom_field_data['create_new_auto_create_expense_custom_fields_destination_attributes_subsequent_run']]
        )
        mock_call.side_effect = [
            expense_custom_field_data['create_new_auto_create_expense_custom_fields_expense_attributes_1'],
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'LUKE').count()

        assert expense_attributes_count == 2

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='LUKE', destination_type='CLASS').count()

        assert mappings_count == 2

        expense_custom_field.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'LUKE').count()

        assert expense_attributes_count == 4

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='LUKE', destination_type='CLASS').count()

        assert mappings_count == 4


def test_construct_fyle_payload(db):
    workspace_id = 5
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    expense_custom_field = ExpenseCustomField(workspace_id, 'LUKE', 'CLASS', None, qbo_connection, ['classes'])
    expense_custom_field.sync_after = None
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials=fyle_credentials)

    # create new case
    paginated_destination_attributes = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CLASS')

    fyle_payload = expense_custom_field.construct_fyle_expense_custom_field_payload(
        paginated_destination_attributes,
        platform,
    )

    assert dict_compare_keys(fyle_payload, expense_custom_field_data['create_fyle_expense_custom_fields_payload_create_new_case']) == [], 'Payload mismatches'
