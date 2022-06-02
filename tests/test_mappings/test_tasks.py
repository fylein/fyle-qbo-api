from asyncio.log import logger
import imp
import pytest
from django_q.models import Schedule
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, CategoryMapping, \
    Mapping, MappingSetting, EmployeeMapping
from apps.mappings.tasks import auto_create_tax_codes_mappings, schedule_tax_groups_creation,auto_create_project_mappings, \
    schedule_projects_creation, remove_duplicates, create_fyle_categories_payload, upload_categories_to_fyle, \
        schedule_categories_creation, auto_create_category_mappings, schedule_cost_centers_creation, auto_map_employees, \
            async_auto_map_employees, schedule_auto_map_employees, auto_map_ccc_employees, async_auto_map_ccc_account, \
                schedule_auto_map_ccc_employees, create_fyle_cost_centers_payload, auto_create_cost_center_mappings, \
                    post_merchants, auto_create_vendors_as_merchants, schedule_vendors_as_merchants_creation,\
                        schedule_fyle_attributes_creation, async_auto_create_custom_field_mappings
from fyle_integrations_platform_connector import PlatformConnector
from apps.mappings.models import GeneralMapping
from .fixtures import data
from tests.helper import dict_compare_keys
from apps.workspaces.models import QBOCredential, FyleCredential, WorkspaceGeneralSettings 


def test_auto_create_tax_codes_mappings(db, mocker):
    workspace_id = 5
    mocker.patch(
        'fyle_integrations_platform_connector.apis.TaxGroups.post_bulk',
        return_value=[]
    )

    tax_groups = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='TAX_CODE').count()
    
    assert tax_groups == 24
    assert mappings == 24
    auto_create_tax_codes_mappings(workspace_id=workspace_id)

    tax_groups = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='TAX_CODE').count()
    assert mappings == 24

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_tax_codes_mappings(workspace_id)

    assert response == None


def test_schedule_tax_groups_creation(db):
    workspace_id = 5
    schedule_tax_groups_creation(import_tax_codes=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_tax_codes_mappings',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.auto_create_tax_codes_mappings'

    schedule_tax_groups_creation(import_tax_codes=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_tax_codes_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_auto_create_project_mappings(db, mocker):
    workspace_id = 3
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Projects.post_bulk',
        return_value=[]
    )
    
    response = auto_create_project_mappings(workspace_id=workspace_id)
    assert response == None

    projects = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='PROJECT').count()

    assert mappings == projects

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_project_mappings(workspace_id=workspace_id)

    assert response == None


@pytest.mark.django_db
def test_schedule_projects_creation(db):
    workspace_id = 3
    schedule_projects_creation(import_to_fyle=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_project_mappings',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.auto_create_project_mappings'

    schedule_projects_creation(import_to_fyle=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_project_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_remove_duplicates(db):

    attributes = DestinationAttribute.objects.filter(attribute_type='EMPLOYEE')
    assert len(attributes) == 19

    attributes = remove_duplicates(attributes)
    assert len(attributes) == 12


def test_create_fyle_category_payload(db):

    qbo_attributes = DestinationAttribute.objects.filter(
        workspace_id=1, attribute_type='ACCOUNT'
    )

    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_category_payload = create_fyle_categories_payload(qbo_attributes, 2)
    assert dict_compare_keys(fyle_category_payload[0], data['fyle_category_payload'][0]) == [], 'category upload api return diffs in keys'


def test_upload_categories_to_fyle(mocker, db):
    workspace_id = 4
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Categories.post_bulk',
        return_value='nilesh'
    )

    qbo_attributes = upload_categories_to_fyle(workspace_id)

    expense_category_count = DestinationAttribute.objects.filter(
        attribute_type='EXPENSE_CATEGORY', workspace_id=workspace_id).count()

    count_of_accounts = DestinationAttribute.objects.filter(
        attribute_type='ACCOUNT', workspace_id=workspace_id).count()
    assert count_of_accounts == 62


def test_auto_create_category_mappings(db, mocker):
    workspace_id = 3
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Categories.post_bulk',
        return_value=[]
    )

    response = auto_create_category_mappings(workspace_id=workspace_id)
    assert response == []

    mappings = CategoryMapping.objects.filter(workspace_id=workspace_id)

    assert len(mappings) == 0

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_category_mappings(workspace_id=workspace_id)

    assert response == None


@pytest.mark.django_db
def test_schedule_categories_creation():
    workspace_id = 3
    schedule_categories_creation(import_categories=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_category_mappings',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.auto_create_category_mappings'

    schedule_categories_creation(import_categories=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_category_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_auto_map_employees(db):
    mappings = auto_map_employees('EMPLOYEE', 'EMAIL', 4)
    assert mappings == None

    mappings = auto_map_employees('EMPLOYEE', 'NAME', 1)
    assert mappings == None


def test_async_auto_map_employees(db):
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

    qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
    qbo_credentials.delete()
    async_auto_map_employees(workspace_id)


def test_schedule_auto_map_employees(db):
    workspace_id = 3
    schedule_auto_map_employees(employee_mapping_preference=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_map_employees',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.async_auto_map_employees'

    schedule_auto_map_employees(employee_mapping_preference=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_map_employees',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_auto_map_ccc_employees(db):
    workspace_id = 3
    auto_map_ccc_employees('41', workspace_id)

    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 17


def test_async_auto_map_ccc_account(db):
    workspace_id = 3
    async_auto_map_ccc_account(workspace_id)

    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 17


def test_schedule_auto_map_ccc_employees(db):
    workspace_id = 3
    schedule_auto_map_ccc_employees(workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_map_ccc_account',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.async_auto_map_ccc_account'

    workspace_id = 1
    schedule_auto_map_ccc_employees(workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_map_ccc_account',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_create_cost_center_payload(db):
    existing_cost_center_names = ExpenseAttribute.objects.filter(
        attribute_type='COST_CENTER', workspace_id=1).values_list('value', flat=True)
    
    qbo_attributes = DestinationAttribute.objects.filter(
        attribute_type='CLASS', workspace_id=1).order_by('value', 'id')     # TODO
    
    qbo_attributes = remove_duplicates(qbo_attributes)

    cost_center_payload = create_fyle_cost_centers_payload(qbo_attributes, existing_cost_center_names)
    assert cost_center_payload == [] 


def test_auto_create_cost_center_mappings(db, mocker):
    workspace_id = 3
    mocker.patch(
            'fyle_integrations_platform_connector.apis.CostCenters.post_bulk',
            return_value=[]
        )
    
    response = auto_create_cost_center_mappings(workspace_id=workspace_id)
    assert response == None

    cost_center = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='DEPARTMENT').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER').count()

    assert cost_center == 0
    assert mappings == 0

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_cost_center_mappings(workspace_id=workspace_id)
    assert response == None


def test_schedule_cost_centers_creation(db):
    workspace_id = 3
    schedule_cost_centers_creation(import_to_fyle=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_cost_center_mappings',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.auto_create_cost_center_mappings'

    schedule_cost_centers_creation(import_to_fyle=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_cost_center_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_schedule_fyle_attributes_creation(db, mocker):
    workspace_id = 4
    schedule_fyle_attributes_creation(workspace_id)

    mocker.patch(
            'fyle_integrations_platform_connector.apis.ExpenseCustomFields.post',
            return_value=[]
    )

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
        args='{}'.format(workspace_id),
    ).first()
    assert schedule.func == 'apps.mappings.tasks.async_auto_create_custom_field_mappings'

    async_auto_create_custom_field_mappings(workspace_id)

    schedule_fyle_attributes_creation(2)
    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule.func == 'apps.mappings.tasks.async_auto_create_custom_field_mappings'


@pytest.mark.django_db
def test_post_merchants(db, mocker):
    workspace_id = 1
    fyle_credentials = FyleCredential.objects.all()
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id) 
    fyle_connection = PlatformConnector(fyle_credentials)

    post_merchants(fyle_connection, workspace_id, False)

    expense_attribute = ExpenseAttribute.objects.filter(attribute_type='MERCHANT', workspace_id=workspace_id).count()
    assert expense_attribute == 24



def test_auto_create_vendors_as_merchants(db, mocker):
    workspace_id = 1
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Merchants.post_bulk',
        return_value=[]
    )

    vendors = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count()
    expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert vendors == 29
    assert expense_attribute == 0

    auto_create_vendors_as_merchants(workspace_id=workspace_id)
    
    vendors = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='VENDOR').count()
    expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='MERCHANT').count()
    assert vendors == 29
    assert expense_attribute == 60

    fyle_credentials = FyleCredential.objects.get(workspace_id=1)
    fyle_credentials.delete()

    response = auto_create_vendors_as_merchants(workspace_id=1)

    assert response == None
    

def test_schedule_vendors_as_merchants_creation(db):
    workspace_id = 2
    schedule_vendors_as_merchants_creation(import_vendors_as_merchants=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_vendors_as_merchants',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.auto_create_vendors_as_merchants'

    schedule_vendors_as_merchants_creation(import_vendors_as_merchants=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_vendors_as_merchants',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None
