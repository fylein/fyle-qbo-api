from unittest import mock

from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping
from fyle_integrations_platform_connector import PlatformConnector

from apps.quickbooks_online.models import QBOSyncTimestamp
from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import FyleCredential, QBOCredential, Workspace
from fyle_integrations_imports.modules.tax_groups import TaxGroup
from tests.test_fyle_integrations_imports.test_modules.fixtures import tax_groups_data


def test_sync_destination_attributes(mocker, db):
    workspace_id = 5

    mocker.patch(
        'qbosdk.apis.TaxCodes.count',
        return_value=10
    )
    mocker.patch(
        'qbosdk.apis.TaxCodes.get_all_generator',
        return_value=[tax_groups_data['create_new_auto_create_tax_groups_destination_attributes']]
    )
    mocker.patch(
        'qbosdk.apis.TaxRates.get_by_id',
        return_value=tax_groups_data['create_new_auto_create_tax_groups_destination_attributes_get_by_id']
    )

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    QBOSyncTimestamp.objects.create(workspace_id=workspace_id)

    Mapping.objects.filter(workspace_id=workspace_id, source_type='TAX_GROUP').delete()
    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').delete()

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    assert destination_attributes_count == 0

    tax_group = TaxGroup(workspace_id, 'TAX_CODE', None,  qbo_connection, ['tax_codes'])
    tax_group.sync_after = None
    tax_group.sync_destination_attributes()

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    assert destination_attributes_count == 1


def test_sync_expense_atrributes(mocker, db):
    workspace_id = 5
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.workspace.fyle_org_id = 'or5qYLrvnoF9'
    fyle_credentials.workspace.save()
    platform = PlatformConnector(fyle_credentials=fyle_credentials)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    Mapping.objects.filter(workspace_id=workspace_id, source_type='TAX_GROUP').delete()
    Mapping.objects.filter(workspace_id=workspace_id, destination_type='TAX_CODE').delete()
    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').delete()
    ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_GROUP').delete()

    tax_group_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_GROUP').count()
    assert tax_group_count == 0

    mocker.patch(
        'fyle.platform.apis.v1.admin.TaxGroups.list_all',
        return_value=[]
    )

    tax_group = TaxGroup(workspace_id, 'TAX_CODE', None,  qbo_connection, ['tax_codes'])
    tax_group.sync_after = None
    tax_group.sync_expense_attributes(platform)

    tax_group_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_GROUP').count()
    assert tax_group_count == 0

    mocker.patch(
        'fyle.platform.apis.v1.admin.TaxGroups.list_all',
        return_value=tax_groups_data['create_new_auto_create_tax_groups_expense_attributes_1']
    )

    tax_group.sync_expense_attributes(platform)

    tax_group_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_GROUP').count()
    assert tax_group_count == 4


def test_auto_create_destination_attributes(mocker, db):
    workspace_id = 5
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    QBOSyncTimestamp.objects.create(workspace_id=workspace_id)

    tax_group = TaxGroup(workspace_id, 'TAX_CODE', None,  qbo_connection, ['tax_codes'])
    tax_group.sync_after = None

    Workspace.objects.filter(id=workspace_id).update(fyle_org_id='or5qYLrvnoF9')

    # delete all destination attributes, expense attributes and mappings
    Mapping.objects.filter(workspace_id=workspace_id, source_type='TAX_GROUP').delete()
    Mapping.objects.filter(workspace_id=workspace_id, destination_type='TAX_CODE').delete()
    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').delete()
    ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_GROUP').delete()

    # create new case for tax-groups import
    with mock.patch('fyle.platform.apis.v1.admin.TaxGroups.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.TaxGroups.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.TaxCodes.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.TaxCodes.get_all_generator',
            return_value=[tax_groups_data['create_new_auto_create_tax_groups_destination_attributes']]
        )
        mocker.patch(
            'qbosdk.apis.TaxRates.get_by_id',
            return_value=tax_groups_data['create_new_auto_create_tax_groups_destination_attributes_get_by_id']
        )
        mock_call.side_effect = [
            tax_groups_data['create_new_auto_create_tax_groups_expense_attributes_0'],
            tax_groups_data['create_new_auto_create_tax_groups_expense_attributes_1']
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'TAX_GROUP').count()

        assert expense_attributes_count == 0

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='TAX_GROUP', destination_type='TAX_CODE').count()

        assert mappings_count == 0

        tax_group.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'TAX_GROUP').count()

        assert expense_attributes_count == 4

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='TAX_GROUP', destination_type='TAX_CODE').count()

        assert mappings_count == 1

    # create subsequen case for tax-groups import
    with mock.patch('fyle.platform.apis.v1.admin.TaxGroups.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.TaxGroups.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.TaxCodes.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.TaxCodes.get_all_generator',
            return_value=[tax_groups_data['create_new_auto_create_tax_groups_destination_attributes_subsequent_case']]
        )
        mocker.patch(
            'qbosdk.apis.TaxRates.get_by_id',
            return_value=tax_groups_data['create_new_auto_create_tax_groups_destination_attributes_get_by_id']
        )
        mocker.patch(
            'qbosdk.apis.TaxRates.get_by_id',
            return_value=tax_groups_data['create_new_auto_create_tax_groups_destination_attributes_subsequent_case_get_by_id']
        )
        mock_call.side_effect = [
            tax_groups_data['create_new_auto_create_tax_groups_expense_attributes_1'],
            tax_groups_data['create_new_auto_create_tax_groups_expense_attributes_2']
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'TAX_GROUP').count()

        assert expense_attributes_count == 4

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='TAX_GROUP', destination_type='TAX_CODE').count()

        assert mappings_count == 1

        tax_group.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'TAX_GROUP').count()

        assert expense_attributes_count == 5

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='TAX_GROUP', destination_type='TAX_CODE').count()

        assert mappings_count == 2


def test_construct_fyle_payload(db):
    workspace_id = 5
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    tax_group = TaxGroup(workspace_id, 'TAX_CODE', None,  qbo_connection, ['tax_codes'])
    tax_group.sync_after = None

    # create new case
    paginated_destination_attributes = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE')
    existing_fyle_attributes_map = {}

    fyle_payload = tax_group.construct_fyle_payload(
        paginated_destination_attributes,
        existing_fyle_attributes_map,
    )

    assert fyle_payload == tax_groups_data['create_fyle_tax_groups_payload_create_new_case']
