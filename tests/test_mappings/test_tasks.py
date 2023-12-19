from unittest import mock

from django_q.models import Schedule
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError
from fyle_accounting_mappings.models import (
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
    schedule_tax_groups_creation,
)
from apps.mappings.tasks import (
    Chain,
    async_auto_map_ccc_account,
    async_auto_map_employees,
    auto_create_tax_codes_mappings,
    auto_create_vendors_as_merchants,
    auto_import_and_map_fyle_fields,
    auto_map_ccc_employees,
    auto_map_employees,
    post_merchants,
    remove_duplicates,
    resolve_expense_attribute_errors,
)
from apps.tasks.models import Error
from apps.workspaces.models import FyleCredential, QBOCredential, WorkspaceGeneralSettings
from tests.test_mappings.fixtures import data


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
