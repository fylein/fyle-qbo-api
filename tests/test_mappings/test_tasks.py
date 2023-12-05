from unittest import mock

from django_q.models import Schedule
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError
from fyle_accounting_mappings.models import (
    CategoryMapping,
    DestinationAttribute,
    EmployeeMapping,
    ExpenseAttribute,
    Mapping,
    MappingSetting,
)
from fyle_integrations_platform_connector import PlatformConnector
from qbosdk.exceptions import WrongParamsError

from apps.mappings.queues import (
    schedule_auto_map_ccc_employees,
    schedule_auto_map_employees,
    schedule_cost_centers_creation,
    schedule_fyle_attributes_creation,
    schedule_tax_groups_creation,
)
from apps.mappings.tasks import (
    Chain,
    async_auto_create_custom_field_mappings,
    async_auto_map_ccc_account,
    async_auto_map_employees,
    auto_create_cost_center_mappings,
    auto_create_expense_fields_mappings,
    auto_create_tax_codes_mappings,
    auto_create_vendors_as_merchants,
    auto_import_and_map_fyle_fields,
    auto_map_ccc_employees,
    auto_map_employees,
    create_fyle_cost_centers_payload,
    post_merchants,
    remove_duplicates,
    resolve_expense_attribute_errors,
)
from apps.tasks.models import Error
from apps.workspaces.models import FyleCredential, QBOCredential, WorkspaceGeneralSettings
from tests.helper import dict_compare_keys
from tests.test_mappings.fixtures import data
from tests.test_fyle.fixtures import data as fyle_data


def test_auto_create_tax_codes_mappings(db, mocker):
    workspace_id = 5
    mocker.patch('qbosdk.apis.TaxCodes.get', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.TaxGroups.post_bulk', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.TaxGroups.sync', return_value=[])

    tax_groups = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='TAX_CODE').count()

    assert tax_groups == 24
    assert mappings == 23
    auto_create_tax_codes_mappings(workspace_id=workspace_id)

    tax_groups = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='TAX_CODE').count()
    assert mappings == 23

    with mock.patch('fyle_integrations_platform_connector.apis.TaxGroups.sync') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='invalid params', response='invalid params')
        auto_create_tax_codes_mappings(workspace_id=workspace_id)

    with mock.patch('fyle_integrations_platform_connector.apis.TaxGroups.sync') as mock_call:
        mock_call.side_effect = FyleInvalidTokenError(msg='Invalid Token for fyle', response='Invalid Token for fyle')
        auto_create_tax_codes_mappings(workspace_id=workspace_id)

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_tax_codes_mappings(workspace_id)
    assert response == None


def test_schedule_tax_groups_creation(db):
    workspace_id = 5
    schedule_tax_groups_creation(import_tax_codes=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.auto_create_tax_codes_mappings', args='{}'.format(workspace_id)).first()

    assert schedule.func == 'apps.mappings.tasks.auto_create_tax_codes_mappings'

    schedule_tax_groups_creation(import_tax_codes=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.auto_create_tax_codes_mappings', args='{}'.format(workspace_id)).first()

    assert schedule == None


def test_remove_duplicates(db):

    attributes = DestinationAttribute.objects.filter(attribute_type='EMPLOYEE')
    assert len(attributes) == 19

    attributes = remove_duplicates(attributes)
    assert len(attributes) == 12


def test_auto_map_employees(db):
    mappings = auto_map_employees('EMPLOYEE', 'EMAIL', 4)
    assert mappings == None

    mappings = auto_map_employees('EMPLOYEE', 'NAME', 2)
    assert mappings == None

    mappings = auto_map_employees('EMPLOYEE', 'EMPLOYEE_CODE', 2)
    assert mappings == None

    mappings = auto_map_employees('VENDOR', 'EMAIL', 2)
    assert mappings == None

    mappings = auto_map_employees('CREDIT_CARD_ACCOUNT', 'NAME', 3)
    assert mappings == None


def test_async_auto_map_employees(mocker, db):
    mocker.patch('qbosdk.apis.Employees.get', return_value=[])
    mocker.patch('qbosdk.apis.Vendors.get', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.Employees.sync', return_value=[])
    workspace_id = 3
    async_auto_map_employees(workspace_id)
    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 4

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    general_settings.employee_field_mapping = 'VENDOR'
    general_settings.save()

    async_auto_map_employees(workspace_id)
    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 4

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_credentials.delete()
    async_auto_map_employees(workspace_id)


def test_schedule_auto_map_employees(db):
    workspace_id = 3
    schedule_auto_map_employees(employee_mapping_preference=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_map_employees', args='{}'.format(workspace_id)).first()

    assert schedule.func == 'apps.mappings.tasks.async_auto_map_employees'

    schedule_auto_map_employees(employee_mapping_preference=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_map_employees', args='{}'.format(workspace_id)).first()

    assert schedule == None


def test_auto_map_ccc_employees(db):
    workspace_id = 3
    auto_map_ccc_employees('41', workspace_id)

    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 17


def test_async_auto_map_ccc_account(mocker, db):
    mocker.patch('fyle_integrations_platform_connector.apis.Employees.sync', return_value=[])
    workspace_id = 3
    async_auto_map_ccc_account(workspace_id)

    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 17


def test_schedule_auto_map_ccc_employees(db):
    workspace_id = 3
    schedule_auto_map_ccc_employees(workspace_id=workspace_id)

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_map_ccc_account', args='{}'.format(workspace_id)).first()

    assert schedule.func == 'apps.mappings.tasks.async_auto_map_ccc_account'

    workspace_id = 1
    schedule_auto_map_ccc_employees(workspace_id=workspace_id)

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_map_ccc_account', args='{}'.format(workspace_id)).first()

    assert schedule == None


def test_create_cost_center_payload(db):
    existing_cost_center_names = ExpenseAttribute.objects.filter(attribute_type='COST_CENTER', workspace_id=4).values_list('value', flat=True)

    qbo_attributes = DestinationAttribute.objects.filter(attribute_type='CLASS', workspace_id=4).first()
    qbo_attributes.value = 'sample333'
    qbo_attributes.save()

    qbo_attributes = DestinationAttribute.objects.filter(attribute_type='CLASS', workspace_id=4).order_by('value', 'id')

    qbo_attributes = remove_duplicates(qbo_attributes)

    cost_center_payload = create_fyle_cost_centers_payload(qbo_attributes, existing_cost_center_names)
    assert cost_center_payload == [{'description': 'Cost Center - sample333, Id - 5000000000000142238', 'is_enabled': True, 'name': 'sample333'}]


def test_auto_create_cost_center_mappings(db, mocker):
    workspace_id = 4
    mocker.patch('qbosdk.apis.Classes.get', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.CostCenters.sync', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.CostCenters.post_bulk', return_value=[])

    qbo_attributes = DestinationAttribute.objects.filter(attribute_type='CLASS', workspace_id=4).first()
    qbo_attributes.value = 'sample333'
    qbo_attributes.save()

    response = auto_create_cost_center_mappings(workspace_id=workspace_id)
    cost_center = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CLASS').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER').count()

    assert cost_center == 5
    assert mappings == 5

    with mock.patch('fyle_integrations_platform_connector.apis.CostCenters.sync') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='invalid params', response='invalid params')
        auto_create_cost_center_mappings(workspace_id)

        mock_call.side_effect = FyleInvalidTokenError(msg='Invalid Token for fyle', response='Invalid Token for fyle')
        auto_create_cost_center_mappings(workspace_id)

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_cost_center_mappings(workspace_id=workspace_id)
    assert response == None


def test_schedule_cost_centers_creation(db):
    workspace_id = 3
    schedule_cost_centers_creation(import_to_fyle=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.auto_create_cost_center_mappings', args='{}'.format(workspace_id)).first()

    assert schedule.func == 'apps.mappings.tasks.auto_create_cost_center_mappings'

    schedule_cost_centers_creation(import_to_fyle=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.auto_create_cost_center_mappings', args='{}'.format(workspace_id)).first()

    assert schedule == None


def test_schedule_fyle_attributes_creation(db, mocker):
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.sync_customers', return_value=None)
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.get_by_id', return_value={'options': ['samp'], 'updated_at': '2020-06-11T13:14:55.201598+00:00'})

    workspace_id = 4
    schedule_fyle_attributes_creation(workspace_id)

    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.post', return_value=[])

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_create_custom_field_mappings', args='{}'.format(workspace_id)).first()
    assert schedule.func == 'apps.mappings.tasks.async_auto_create_custom_field_mappings'

    async_auto_create_custom_field_mappings(workspace_id)

    mapping_settings = MappingSetting.objects.filter(is_custom=True, import_to_fyle=True, workspace_id=workspace_id)
    mapping_settings.delete()

    schedule_fyle_attributes_creation(workspace_id)
    schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_create_custom_field_mappings', args='{}'.format(workspace_id)).first()

    assert schedule == None

    mocker.patch('apps.mappings.tasks.upload_attributes_to_fyle', return_value=['CUSTOMER'])

    with mock.patch('fyle_accounting_mappings.models.Mapping.bulk_create_mappings') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='invalid params', response='invalid params')
        auto_create_expense_fields_mappings(workspace_id, 'CUSTOMER', 'CUSTOMER', 'Select CUSTOMER')


def test_post_merchants(db, mocker):
    mocker.patch('fyle_integrations_platform_connector.apis.Merchants.get', return_value=data['get_merchants'])
    mocker.patch('fyle_integrations_platform_connector.apis.Merchants.post', return_value=[])
    mocker.patch('fyle.platform.apis.v1beta.admin.expense_fields', return_value=data['get_merchants'])
    workspace_id = 5
    fyle_credentials = FyleCredential.objects.all()
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_connection = PlatformConnector(fyle_credentials)

    post_merchants(fyle_connection, workspace_id)

    expense_attribute = ExpenseAttribute.objects.filter(attribute_type='MERCHANT', workspace_id=workspace_id).count()
    assert expense_attribute == 44


def test_auto_create_vendors_as_merchants(db, mocker):
    workspace_id = 1
    mocker.patch('fyle_integrations_platform_connector.apis.Merchants.sync', return_value=[])
    mocker.patch('fyle_integrations_platform_connector.apis.Merchants.post', return_value=[])
    mocker.patch('qbosdk.apis.Vendors.get', return_value=[])

    vendors = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count()
    expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert vendors == 29
    assert expense_attribute == 0

    auto_create_vendors_as_merchants(workspace_id=workspace_id)

    vendors = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count()
    expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert vendors == 29
    assert expense_attribute == 0

    with mock.patch('fyle_integrations_platform_connector.apis.Merchants.sync') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='invalid params', response='invalid params')
        auto_create_vendors_as_merchants(workspace_id=workspace_id)

        mock_call.side_effect = FyleInvalidTokenError(msg='Invalid Token for fyle', response='Invalid Token for fyle')
        auto_create_vendors_as_merchants(workspace_id=workspace_id)

    fyle_credentials = FyleCredential.objects.get(workspace_id=1)
    fyle_credentials.delete()

    response = auto_create_vendors_as_merchants(workspace_id=1)

    assert response == None


def test_resolve_expense_attribute_errors(db):
    workspace_id = 3
    errors = Error.objects.filter(workspace_id=workspace_id, type='EMPLOYEE_MAPPING', expense_attribute_id=5327, is_resolved=False).count()
    assert errors == 1

    resolve_expense_attribute_errors('EMPLOYEE', workspace_id, 'VENDOR')

    errors = Error.objects.filter(workspace_id=workspace_id, type='EMPLOYEE_MAPPING', expense_attribute_id=5327, is_resolved=False).count()
    assert errors == 0


def test_auto_import_and_map_fyle_field(db, mocker):
    workspace_id = 3
    mocker.patch.object(WorkspaceGeneralSettings.objects, 'get', return_value=WorkspaceGeneralSettings(workspace_id=workspace_id))
    mocker.patch.object(MappingSetting.objects, 'filter', return_value=MappingSetting.objects.none())

    chain_mock = mocker.Mock(Chain)
    mocker.patch.object(Chain, 'append', return_value=chain_mock)
    mocker.patch.object(chain_mock, 'length', return_value=0)

    vendors = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count()
    expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert vendors == 29
    assert expense_attribute == 89

    auto_import_and_map_fyle_fields(workspace_id=workspace_id)

    vendors = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count()
    expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert vendors == 29
    assert expense_attribute == 89

    mocker.patch.object(MappingSetting.objects, 'filter', return_value=MappingSetting.objects.all()[:1])
    mocker.patch.object(Chain, 'run')
