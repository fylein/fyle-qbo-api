import pytest
from django_q.models import Schedule
from fyle_accounting_mappings.models import EmployeeMapping, ExpenseAttribute, Mapping, MappingSetting

from apps.fyle.models import ExpenseGroupSettings
from apps.tasks.models import Error
from tests.test_fyle.fixtures import data as fyle_data


def test_resolve_post_mapping_errors(test_connection, mocker, db):
    category_attribute = ExpenseAttribute.objects.filter(value='WET Paid', workspace_id=3, attribute_type='CATEGORY').first()

    Error.objects.update_or_create(workspace_id=3, expense_attribute=category_attribute, defaults={'type': 'CATEGORY_MAPPING', 'error_title': category_attribute.value, 'error_detail': 'Category mapping is missing', 'is_resolved': False})

    mapping = Mapping(
        source_type='CATEGORY',
        destination_type='ACCOUNT',
        # source__value=source_value,
        source_id=5322,
        destination_id=585,
        workspace_id=3,
    )
    mapping.save()
    error = Error.objects.filter(expense_attribute_id=mapping.source_id).first()

    assert error.is_resolved == True


@pytest.mark.django_db()
def test_resolve_post_employees_mapping_errors(test_connection, db):
    source_employee = ExpenseAttribute.objects.filter(
        value='ashwin.t+1@fyle.in',
        workspace_id=2,
        attribute_type='EMPLOYEE'
    ).first()

    Error.objects.update_or_create(
        workspace_id=2,
        expense_attribute=source_employee,
        defaults={
            'type': 'EMPLOYEE_MAPPING',
            'error_title': source_employee.value,
            'error_detail': 'Employee mapping is missing',
            'is_resolved': False
        }
    )
    employee_mapping = EmployeeMapping.objects.get(
       source_employee_id=2082,
        workspace_id=2
    )
    employee_mapping.destination_employee_id = 748
    employee_mapping.save()

    error = Error.objects.filter(expense_attribute_id=employee_mapping.source_employee_id).first()

    assert error.is_resolved == True


@pytest.mark.django_db()
def test_run_post_mapping_settings_triggers(test_connection, mocker):
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.post', return_value=[])

    mocker.patch('fyle.platform.apis.v1beta.admin.ExpenseFields.list_all', return_value=fyle_data['get_all_expense_fields'])

    mapping_setting = MappingSetting(source_field='PROJECT', destination_field='PROJECT', workspace_id=2, import_to_fyle=True, is_custom=False)

    mapping_setting.save()

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.auto_create_project_mappings', args='{}'.format(2)).first()

    assert schedule.func == 'apps.mappings.tasks.auto_create_project_mappings'
    assert schedule.args == '2'

    mapping_setting = MappingSetting(source_field='COST_CENTER', destination_field='CLASS', workspace_id=1, import_to_fyle=True, is_custom=False)

    mapping_setting.save()

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.auto_create_cost_center_mappings', args='{}'.format(1)).first()

    assert schedule.func == 'apps.mappings.tasks.auto_create_cost_center_mappings'
    assert schedule.args == '1'

    mapping_setting = MappingSetting(source_field='PROJECT', destination_field='DEPARTMENT', workspace_id=1, import_to_fyle=False, is_custom=False)

    mapping_setting.save()

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=1)
    assert 'project' in expense_group_settings.reimbursable_expense_group_fields
    assert 'project' in expense_group_settings.corporate_credit_card_expense_group_fields

    mapping_setting = MappingSetting(source_field='SAMPLEs', destination_field='SAMPLEs', workspace_id=1, import_to_fyle=True, is_custom=True)
    mapping_setting.save()

    schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_create_custom_field_mappings', args='{}'.format(1)).first()

    assert schedule.func == 'apps.mappings.tasks.async_auto_create_custom_field_mappings'
    assert schedule.args == '1'


@pytest.mark.django_db()
def test_run_post_delete_mapping_settings_triggers(test_connection):
    mapping_setting = MappingSetting(source_field='COST_CENTER', destination_field='DEPARTMENT', workspace_id=1, import_to_fyle=False, is_custom=False)

    mapping_setting.save()

    mapping_setting.delete()

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=1)
    assert 'cost_center' not in expense_group_settings.reimbursable_expense_group_fields
    assert 'cost_center' not in expense_group_settings.corporate_credit_card_expense_group_fields


def test_run_pre_mapping_settings_triggers(db, mocker, test_connection):
    mocker.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.post', return_value=[])

    mocker.patch('fyle.platform.apis.v1beta.admin.ExpenseFields.list_all', return_value=fyle_data['get_all_expense_fields'])

    workspace_id = 1

    custom_mappings = Mapping.objects.filter(workspace_id=workspace_id, source_type='CUSTOM_INTENTs').count()
    assert custom_mappings == 0

    mapping_setting = MappingSetting(source_field='CUSTOM_INTENTs', destination_field='CUSTOM_INTENTs', workspace_id=workspace_id, import_to_fyle=True, is_custom=True)
    mapping_setting.save()

    custom_mappings = Mapping.objects.last()

    custom_mappings = Mapping.objects.filter(workspace_id=workspace_id, source_type='CUSTOM_INTENTs').count()
    assert custom_mappings == 0
