from django_q.models import Schedule
from fyle_accounting_mappings.models import (
    EmployeeMapping,
)

from apps.mappings.queues import (
    schedule_auto_map_ccc_employees,
    schedule_auto_map_employees
)
from apps.mappings.tasks import (
    async_auto_map_ccc_account,
    async_auto_map_employees,
    auto_map_ccc_employees,
    auto_map_employees,
    resolve_expense_attribute_errors,
)
from apps.tasks.models import Error
from apps.workspaces.models import QBOCredential, WorkspaceGeneralSettings
from fyle.platform.exceptions import (
    InvalidTokenError as FyleInvalidTokenError,
    InternalServerError
)


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
    mocker.patch('apps.mappings.exceptions.invalidate_qbo_credentials', return_value=None)
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
    mock_call = mocker.patch('fyle_integrations_platform_connector.apis.Employees.sync', return_value=[])
    workspace_id = 3
    async_auto_map_ccc_account(workspace_id)

    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 17

    mock_call.side_effect = FyleInvalidTokenError('Invalid Token')
    async_auto_map_ccc_account(workspace_id)

    mock_call.side_effect = InternalServerError('Internal Server Error')
    async_auto_map_ccc_account(workspace_id)

    assert mock_call.call_count == 3


def test_schedule_auto_map_ccc_employees(db):
    workspace_id = 3
    schedule_auto_map_ccc_employees(workspace_id=workspace_id)

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_map_ccc_account', args='{}'.format(workspace_id)).first()

    assert schedule.func == 'apps.mappings.tasks.async_auto_map_ccc_account'

    workspace_id = 1
    schedule_auto_map_ccc_employees(workspace_id=workspace_id)

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_map_ccc_account', args='{}'.format(workspace_id)).first()

    assert schedule == None


def test_resolve_expense_attribute_errors(db):
    workspace_id = 3
    errors = Error.objects.filter(workspace_id=workspace_id, type='EMPLOYEE_MAPPING', expense_attribute_id=5327, is_resolved=False).count()
    assert errors == 1

    resolve_expense_attribute_errors('EMPLOYEE', workspace_id, 'VENDOR')

    errors = Error.objects.filter(workspace_id=workspace_id, type='EMPLOYEE_MAPPING', expense_attribute_id=5327, is_resolved=False).count()
    assert errors == 0
