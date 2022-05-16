import logging
import traceback
from dateutil import parser
from datetime import datetime, timedelta

from typing import List, Dict

from django_q.models import Schedule

from fylesdk import WrongParamsError
from fyle_integrations_platform_connector import PlatformConnector
from fyle_accounting_mappings.models import MappingSetting, Mapping, DestinationAttribute, ExpenseAttribute,\
    EmployeeMapping

from apps.fyle.utils import FyleConnector
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import QBOCredential, FyleCredential, WorkspaceGeneralSettings
from apps.tasks.models import Error

from .constants import FYLE_EXPENSE_SYSTEM_FIELDS

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def resolve_expense_attribute_errors(
    source_attribute_type: str, workspace_id: int, destination_attribute_type: str = None):
    """
    Resolve Expense Attribute Errors
    :return: None
    """
    errored_attribute_ids: List[int] = Error.objects.filter(
        is_resolved=False,
        workspace_id=workspace_id,
        type='{}_MAPPING'.format(source_attribute_type)
    ).values_list('expense_attribute_id', flat=True)

    if errored_attribute_ids:
        mapped_attribute_ids = []

        if source_attribute_type == 'CATEGORY':
            mapped_attribute_ids: List[int] = Mapping.objects.filter(
                source_id__in=errored_attribute_ids
            ).values_list('source_id', flat=True)

        elif source_attribute_type == 'EMPLOYEE':
            if destination_attribute_type == 'EMPLOYEE':
                params = {
                    'source_employee_id__in': errored_attribute_ids,
                    'destination_employee_id__isnull': False
                }
            else:
                params = {
                    'source_employee_id__in': errored_attribute_ids,
                    'destination_vendor_id__isnull': False
                }
            mapped_attribute_ids: List[int] = EmployeeMapping.objects.filter(**params).values_list(
                'source_employee_id', flat=True
            )

        if mapped_attribute_ids:
            Error.objects.filter(expense_attribute_id__in=mapped_attribute_ids).update(is_resolved=True)


def remove_duplicates(qbo_attributes: List[DestinationAttribute]):
    unique_attributes = []

    attribute_values = []

    for attribute in qbo_attributes:
        if attribute.value not in attribute_values:
            unique_attributes.append(attribute)
            attribute_values.append(attribute.value)

    return unique_attributes


def create_fyle_projects_payload(projects: List[DestinationAttribute], existing_project_names: list):
    """
    Create Fyle Projects Payload from QBO Customer / Projects
    :param projects: QBO Projects
    :param existing_project_names: Existing Projects in Fyle
    :return: Fyle Projects Payload
    """
    payload = []

    for project in projects:
        if project.value not in existing_project_names:
            payload.append({
                'name': project.value,
                'code': project.destination_id,
                'description': 'Project - {0}, Id - {1}'.format(
                    project.value,
                    project.destination_id
                ),
                'is_enabled': True if project.active is None else project.active
            })

    return payload


def post_projects_in_batches(platform: PlatformConnector, workspace_id: int, destination_field: str):
    existing_project_names = ExpenseAttribute.objects.filter(
        attribute_type='PROJECT', workspace_id=workspace_id).values_list('value', flat=True)
    qbo_attributes_count = DestinationAttribute.objects.filter(
        attribute_type=destination_field, workspace_id=workspace_id).count()

    page_size = 200
    for offset in range(0, qbo_attributes_count, page_size):
        limit = offset + page_size
        paginated_qbo_attributes = DestinationAttribute.objects.filter(
            attribute_type=destination_field, workspace_id=workspace_id).order_by('value', 'id')[offset:limit]

        paginated_qbo_attributes = remove_duplicates(paginated_qbo_attributes)

        fyle_payload: List[Dict] = create_fyle_projects_payload(paginated_qbo_attributes, existing_project_names)
        if fyle_payload:
            platform.projects.post_bulk(fyle_payload)
            platform.projects.sync()

        Mapping.bulk_create_mappings(paginated_qbo_attributes, 'PROJECT', destination_field, workspace_id)


def auto_create_tax_codes_mappings(workspace_id: int):
    """
    Create Tax Codes Mappings
    :return: None
    """
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

        platform = PlatformConnector(fyle_credentials)

        platform.tax_groups.sync()

        mapping_setting = MappingSetting.objects.get(
            source_field='TAX_GROUP', workspace_id=workspace_id
        )

        sync_qbo_attribute(mapping_setting.destination_field, workspace_id)
        upload_tax_groups_to_fyle(platform, workspace_id)

    except WrongParamsError as exception:
        logger.error(
            'Error while creating tax groups workspace_id - %s in Fyle %s %s',
            workspace_id, exception.message, {'error': exception.response}
        )

    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.error(
            'Error while creating tax groups workspace_id - %s error: %s',
            workspace_id, error
        )


def auto_create_project_mappings(workspace_id: int):
    """
    Create Project Mappings
    :return: mappings
    """
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)
        platform = PlatformConnector(fyle_credentials)

        platform.projects.sync()

        mapping_setting = MappingSetting.objects.get(
            source_field='PROJECT', workspace_id=workspace_id
        )

        sync_qbo_attribute(mapping_setting.destination_field, workspace_id)

        post_projects_in_batches(platform, workspace_id, mapping_setting.destination_field)

    except WrongParamsError as exception:
        logger.error(
            'Error while creating projects workspace_id - %s in Fyle %s %s',
            workspace_id, exception.message, {'error': exception.response}
        )

    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.exception(
            'Error while creating projects workspace_id - %s error: %s',
            workspace_id, error
        )


def schedule_tax_groups_creation(import_tax_codes, workspace_id):
    if import_tax_codes:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_tax_codes_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_tax_codes_mappings',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_projects_creation(import_to_fyle, workspace_id):
    if import_to_fyle:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_project_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 6 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_project_mappings',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def create_fyle_categories_payload(categories: List[DestinationAttribute], workspace_id: int):
    """
    Create Fyle Categories Payload from QBO Customer / Categories
    :param workspace_id: Workspace integer id
    :param categories: QBO Categories
    :return: Fyle Categories Payload
    """
    payload = []

    existing_category_names = ExpenseAttribute.objects.filter(
        attribute_type='CATEGORY', workspace_id=workspace_id).values_list('value', flat=True)

    for category in categories:
        if category.value not in existing_category_names:
            payload.append({
                'name': category.value,
                'code': category.destination_id,
                'is_enabled': True if category.active is None else category.active,
                'restricted_project_ids': None
            })

    return payload


def upload_categories_to_fyle(workspace_id):
    """
    Upload categories to Fyle
    """
    fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)
    qbo_credentials: QBOCredential = QBOCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)

    qbo_connection = QBOConnector(
        credentials_object=qbo_credentials,
        workspace_id=workspace_id
    )
    platform.categories.sync()
    qbo_connection.sync_accounts()
    general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    qbo_attributes: List[DestinationAttribute] = DestinationAttribute.objects.filter(
        workspace_id=workspace_id, attribute_type='ACCOUNT', detail__account_type__in=general_settings.charts_of_accounts).all()
    qbo_attributes = remove_duplicates(qbo_attributes)
    fyle_payload: List[Dict] = create_fyle_categories_payload(qbo_attributes, workspace_id)

    if fyle_payload:
        platform.categories.post_bulk(fyle_payload)
        platform.categories.sync()

    return qbo_attributes


def auto_create_category_mappings(workspace_id):
    """
    Create Category Mappings
    :return: mappings
    """
    try:
        fyle_categories = upload_categories_to_fyle(workspace_id=workspace_id)
        category_mappings = Mapping.bulk_create_mappings(fyle_categories, 'CATEGORY', 'ACCOUNT', workspace_id)
        resolve_expense_attribute_errors(
            source_attribute_type='CATEGORY',
            workspace_id=workspace_id
        )
        return category_mappings
    except WrongParamsError as exception:
        logger.error(
            'Error while creating categories workspace_id - %s in Fyle %s %s',
            workspace_id, exception.message, {'error': exception.response}
        )

    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.exception(
            'Error while creating categories workspace_id - %s error: %s',
            workspace_id, error
        )


def schedule_categories_creation(import_categories, workspace_id):
    if import_categories:
        start_datetime = datetime.now()
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_category_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_category_mappings',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def get_existing_source_and_mappings(destination_type: str, workspace_id: int):
    existing_mappings = EmployeeMapping.objects.filter(
        workspace_id=workspace_id
    ).all()

    existing_source_ids = []
    for mapping in existing_mappings:
        destination = None
        if destination_type == 'EMPLOYEE':
            destination = mapping.destination_employee
        elif destination_type == 'VENDOR':
            destination = mapping.destination_vendor
        elif destination_type == 'CREDIT_CARD_ACCOUNT':
            destination = mapping.destination_card_account

        if destination:
            existing_source_ids.append(mapping.source_employee.id)

    return existing_source_ids, existing_mappings


def check_exact_matches(employee_mapping_preference: str, source_attribute: ExpenseAttribute,
    destination_id_value_map: dict, destination_type: str):
    """
    Check if the source attribute matches with the destination attribute
    :param employee_mapping_preference: Employee Mapping Preference
    :param source_attribute: Source Attribute
    :param destination_id_value_map: Destination ID Value Map
    :param destination_type: Destination Type
    :return: Destination Column and value if exact match found
    """
    source_value = ''
    destination = {}
    if employee_mapping_preference == 'EMAIL':
        source_value = source_attribute.value
    elif employee_mapping_preference == 'NAME':
        source_value = source_attribute.detail['full_name']
    elif employee_mapping_preference == 'EMPLOYEE_CODE':
        source_value = source_attribute.detail['employee_code']

    # Handling employee_code or full_name null case
    if not source_value:
        source_value = ''

    # Checking exact match
    if source_value.lower() in destination_id_value_map:
        if destination_type == 'EMPLOYEE':
            destination['destination_employee_id'] = destination_id_value_map[source_value.lower()]
        elif destination_type == 'VENDOR':
            destination['destination_vendor_id'] = destination_id_value_map[source_value.lower()]
        elif destination_type == 'CREDIT_CARD_ACCOUNT':
            destination['destination_card_account_id'] = destination_id_value_map[source_value.lower()]

    return destination


def construct_mapping_payload(employee_source_attributes: List[ExpenseAttribute], employee_mapping_preference: str,
                              destination_id_value_map: dict, destination_type: str, workspace_id: int):
    """
    Construct mapping payload
    :param employee_source_attributes: Employee Source Attributes
    :param employee_mapping_preference: Employee Mapping Preference
    :param destination_id_value_map: Destination ID Value Map
    :param destination_type: Destination Type
    :param workspace_id: Workspace ID
    :return: mapping_creation_batch, mapping_updation_batch, update_key
    """
    existing_source_ids, existing_mappings = get_existing_source_and_mappings(destination_type, workspace_id)

    mapping_creation_batch = []
    mapping_updation_batch = []
    update_key = None
    existing_mappings_map = {mapping.source_employee_id: mapping.id for mapping in existing_mappings}

    for source_attribute in employee_source_attributes:
        # Ignoring already present mappings
        if source_attribute.id not in existing_source_ids:
            destination = check_exact_matches(employee_mapping_preference, source_attribute,
                destination_id_value_map, destination_type)
            if destination:
                update_key = list(destination.keys())[0]
                if source_attribute.id in existing_mappings_map:
                    # If employee mapping row exists, then update it
                    mapping_updation_batch.append(
                        EmployeeMapping(
                            id=existing_mappings_map[source_attribute.id],
                            source_employee=source_attribute,
                            **destination
                        )
                    )
                else:
                    # If employee mapping row does not exist, then create it
                    mapping_creation_batch.append(
                        EmployeeMapping(
                            source_employee_id=source_attribute.id,
                            workspace_id=workspace_id,
                            **destination
                        )
                    )

    return mapping_creation_batch, mapping_updation_batch, update_key


def create_mappings_and_update_flag(mapping_creation_batch: List[EmployeeMapping],
    mapping_updation_batch: List[EmployeeMapping], update_key: str):
    """
    Create Mappings and Update Flag
    :param mapping_creation_batch: Mapping Creation Batch
    :param mapping_updation_batch: Mapping Updation Batch
    :param update_key: Update Key
    :return: created mappings
    """
    mappings = []

    if mapping_creation_batch:
        created_mappings = EmployeeMapping.objects.bulk_create(mapping_creation_batch, batch_size=50)
        mappings.extend(created_mappings)

    if mapping_updation_batch:
        EmployeeMapping.objects.bulk_update(
            mapping_updation_batch, fields=[update_key], batch_size=50
        )
        for mapping in mapping_updation_batch:
            mappings.append(mapping)

    expense_attributes_to_be_updated = []

    for mapping in mappings:
        expense_attributes_to_be_updated.append(
            ExpenseAttribute(
                id=mapping.source_employee.id,
                auto_mapped=True
            )
        )

    if expense_attributes_to_be_updated:
        ExpenseAttribute.objects.bulk_update(
            expense_attributes_to_be_updated, fields=['auto_mapped'], batch_size=50)

    return mappings


def auto_map_employees(destination_type: str, employee_mapping_preference: str, workspace_id: int):
    """
    Auto map employees
    :param destination_type: Destination Type of mappings
    :param employee_mapping_preference: Employee Mapping Preference
    :param workspace_id: Workspace ID
    """
    # Filtering only not mapped destination attributes
    employee_destination_attributes = DestinationAttribute.objects.filter(
        attribute_type=destination_type, workspace_id=workspace_id).all()

    destination_id_value_map = {}
    for destination_employee in employee_destination_attributes:
        value_to_be_appended = None
        if employee_mapping_preference == 'EMAIL' and destination_employee.detail \
                and destination_employee.detail['email']:
            value_to_be_appended = destination_employee.detail['email'].replace('*', '')
        elif employee_mapping_preference in ['NAME', 'EMPLOYEE_CODE']:
            value_to_be_appended = destination_employee.value.replace('*', '')

        if value_to_be_appended:
            destination_id_value_map[value_to_be_appended.lower()] = destination_employee.id

    filters = {
        'attribute_type': 'EMPLOYEE',
        'workspace_id': workspace_id
    }

    if destination_type == 'VENDOR':
        filters['employeemapping__destination_vendor__isnull'] = True
    else:
        filters['employeemapping__destination_employee__isnull'] = True

    employee_source_attributes_count = ExpenseAttribute.objects.filter(**filters).count()
    page_size = 200
    employee_source_attributes = []

    for offset in range(0, employee_source_attributes_count, page_size):
        limit = offset + page_size
        paginated_employee_source_attributes = ExpenseAttribute.objects.filter(**filters)[offset:limit]
        employee_source_attributes.extend(paginated_employee_source_attributes)

    mapping_creation_batch, mapping_updation_batch, update_key = construct_mapping_payload(
        employee_source_attributes, employee_mapping_preference,
        destination_id_value_map, destination_type, workspace_id
    )

    create_mappings_and_update_flag(mapping_creation_batch, mapping_updation_batch, update_key)


def async_auto_map_employees(workspace_id: int):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    employee_mapping_preference = general_settings.auto_map_employees
    destination_type = general_settings.employee_field_mapping

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)

    try:
        qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
        qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

        platform.employees.sync()
        if destination_type == 'EMPLOYEE':
            qbo_connection.sync_employees()
        else:
            qbo_connection.sync_vendors()

        auto_map_employees(destination_type, employee_mapping_preference, workspace_id)

        resolve_expense_attribute_errors(
            source_attribute_type='EMPLOYEE',
            workspace_id=workspace_id ,
            destination_attribute_type=destination_type
        )
    except QBOCredential.DoesNotExist:
        logger.error(
            'QBO Credentials not found for workspace_id %s', workspace_id
        )


def schedule_auto_map_employees(employee_mapping_preference: str, workspace_id: int):
    if employee_mapping_preference:
        start_datetime = datetime.now()

        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.async_auto_map_employees',
            args='{0}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_map_employees',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def auto_map_ccc_employees(default_ccc_account_id: str, workspace_id: int):
    """
    Auto map ccc employees
    :param default_ccc_account_id: Default CCC Account ID
    :param workspace_id: Workspace ID
    """
    employee_source_attributes = ExpenseAttribute.objects.filter(
        attribute_type='EMPLOYEE', workspace_id=workspace_id
    ).all()

    default_destination_attribute = DestinationAttribute.objects.filter(
        destination_id=default_ccc_account_id, workspace_id=workspace_id, attribute_type='CREDIT_CARD_ACCOUNT'
    ).first()

    existing_source_ids, existing_mappings = get_existing_source_and_mappings('CREDIT_CARD_ACCOUNT', workspace_id)
    existing_mappings_map = {mapping.source_employee_id: mapping.id for mapping in existing_mappings}

    mapping_creation_batch = []
    mapping_updation_batch = []
    for source_employee in employee_source_attributes:
        # Ignoring already present mappings
        if source_employee.id not in existing_source_ids:
            if source_employee.id in existing_mappings_map:
                # If employee mapping row exists, then update it
                mapping_updation_batch.append(
                    EmployeeMapping(
                        id=existing_mappings_map[source_employee.id],
                        destination_card_account_id=default_destination_attribute.id
                    )
                )
            else:
                # If employee mapping row does not exist, then create it
                mapping_creation_batch.append(
                    EmployeeMapping(
                        source_employee_id=source_employee.id,
                        destination_card_account_id=default_destination_attribute.id,
                        workspace_id=workspace_id
                    )
                )

    if mapping_creation_batch:
        EmployeeMapping.objects.bulk_create(mapping_creation_batch, batch_size=50)

    if mapping_updation_batch:
        EmployeeMapping.objects.bulk_update(
            mapping_updation_batch, fields=['destination_card_account_id'], batch_size=50
        )


def async_auto_map_ccc_account(workspace_id: int):
    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    if general_mappings:
        default_ccc_account_id = general_mappings.default_ccc_account_id

        if default_ccc_account_id:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            platform = PlatformConnector(fyle_credentials)

            platform.employees.sync()

            auto_map_ccc_employees(default_ccc_account_id, workspace_id)


def schedule_auto_map_ccc_employees(workspace_id: int):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    if general_settings.auto_map_employees and general_settings.corporate_credit_card_expenses_object != 'BILL':
        start_datetime = datetime.now()

        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.async_auto_map_ccc_account',
            args='{0}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_map_ccc_account',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def upload_tax_groups_to_fyle(platform_connection: PlatformConnector, workspace_id: int):
    existing_tax_codes_name = ExpenseAttribute.objects.filter(
        attribute_type='TAX_GROUP', workspace_id=workspace_id).values_list('value', flat=True)

    qbo_attributes = DestinationAttribute.objects.filter(
        attribute_type='TAX_CODE', workspace_id=workspace_id).order_by('value', 'id')

    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_payload: List[Dict] = create_fyle_tax_group_payload(qbo_attributes, existing_tax_codes_name)

    if fyle_payload:
        platform_connection.tax_groups.post_bulk(fyle_payload)

    platform_connection.tax_groups.sync()
    Mapping.bulk_create_mappings(qbo_attributes, 'TAX_GROUP', 'TAX_CODE', workspace_id)


def sync_qbo_attribute(qbo_attribute_type: str, workspace_id: int):
    qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    if qbo_attribute_type == 'CUSTOMER':
        qbo_connection.sync_customers()

    elif qbo_attribute_type == 'DEPARTMENT':
        qbo_connection.sync_departments()

    elif qbo_attribute_type == 'CLASS':
        qbo_connection.sync_classes()
    
    elif qbo_attribute_type == 'TAX_CODE':
        qbo_connection.sync_tax_codes()

    elif qbo_attribute_type == 'VENDOR':
        qbo_connection.sync_vendors()


def create_fyle_cost_centers_payload(qbo_attributes: List[DestinationAttribute], existing_fyle_cost_centers: list):
    """
    Create Fyle Cost Centers Payload from QBO Objects
    :param existing_fyle_cost_centers: Existing cost center names
    :param qbo_attributes: QBO Objects
    :return: Fyle Cost Centers Payload
    """
    fyle_cost_centers_payload = []

    for qbo_attribute in qbo_attributes:
        if qbo_attribute.value not in existing_fyle_cost_centers:
            fyle_cost_centers_payload.append({
                'name': qbo_attribute.value,
                'is_enabled': True if qbo_attribute.active is None else qbo_attribute.active,
                'description': 'Cost Center - {0}, Id - {1}'.format(
                    qbo_attribute.value,
                    qbo_attribute.destination_id
                )
            })

    return fyle_cost_centers_payload


def create_fyle_tax_group_payload(qbo_attributes: List[DestinationAttribute], existing_fyle_tax_groups: list):
    """
    Create Fyle Cost Centers Payload from QBO Objects
    :param existing_fyle_tax_groups: Existing cost center names
    :param qbo_attributes: QBO Objects
    :return: Fyle Cost Centers Payload
    """

    fyle_tax_group_payload = []
    for qbo_attribute in qbo_attributes:
        if qbo_attribute.value not in existing_fyle_tax_groups:
            fyle_tax_group_payload.append({
                    'name': qbo_attribute.value,
                    'is_enabled': True,
                    'percentage': round((qbo_attribute.detail['tax_rate']/100), 2)
                })

    return fyle_tax_group_payload


def post_cost_centers_in_batches(platform: PlatformConnector, workspace_id: int, qbo_attribute_type: str):
    existing_cost_center_names = ExpenseAttribute.objects.filter(
        attribute_type='COST_CENTER', workspace_id=workspace_id).values_list('value', flat=True)

    qbo_attributes_count = DestinationAttribute.objects.filter(
        attribute_type=qbo_attribute_type, workspace_id=workspace_id).count()

    page_size = 200

    for offset in range(0, qbo_attributes_count, page_size):
        limit = offset + page_size
        paginated_qbo_attributes = DestinationAttribute.objects.filter(
            attribute_type=qbo_attribute_type, workspace_id=workspace_id).order_by('value', 'id')[offset:limit]

        paginated_qbo_attributes = remove_duplicates(paginated_qbo_attributes)

        fyle_payload: List[Dict] = create_fyle_cost_centers_payload(
            paginated_qbo_attributes, existing_cost_center_names)

        if fyle_payload:
            platform.cost_centers.post_bulk(fyle_payload)
            platform.cost_centers.sync()

        Mapping.bulk_create_mappings(paginated_qbo_attributes, 'COST_CENTER', qbo_attribute_type, workspace_id)


def auto_create_cost_center_mappings(workspace_id):
    """
    Create Cost Center Mappings
    """
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

        platform = PlatformConnector(fyle_credentials)

        mapping_setting = MappingSetting.objects.get(
            source_field='COST_CENTER', import_to_fyle=True, workspace_id=workspace_id
        )

        platform.cost_centers.sync()

        sync_qbo_attribute(mapping_setting.destination_field, workspace_id)

        post_cost_centers_in_batches(platform, workspace_id, mapping_setting.destination_field)

    except WrongParamsError as exception:
        logger.error(
            'Error while creating cost centers workspace_id - %s in Fyle %s %s',
            workspace_id, exception.message, {'error': exception.response}
        )

    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.exception(
            'Error while creating cost centers workspace_id - %s error: %s',
            workspace_id, error
        )


def schedule_cost_centers_creation(import_to_fyle, workspace_id):
    if import_to_fyle:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_cost_center_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_cost_center_mappings',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def create_fyle_expense_custom_field_payload(
    qbo_attributes: List[DestinationAttribute], workspace_id: int,
    fyle_attribute: str, source_placeholder: str = None
):
    """
    Create Fyle Expense Custom Field Payload from QBO Objects
    :param workspace_id: Workspace ID
    :param qbo_attributes: QBO Objects
    :param fyle_attribute: Fyle Attribute
    :return: Fyle Expense Custom Field Payload
    """
    fyle_expense_custom_field_options = []

    [fyle_expense_custom_field_options.append(qbo_attribute.value) for qbo_attribute in qbo_attributes]

    if fyle_attribute.lower() not in FYLE_EXPENSE_SYSTEM_FIELDS:
        existing_attribute = ExpenseAttribute.objects.filter(
            attribute_type=fyle_attribute, workspace_id=workspace_id).values_list('detail', flat=True).first()

        custom_field_id = None
        placeholder = None
        if existing_attribute is not None:
            custom_field_id = existing_attribute['custom_field_id']
            placeholder = existing_attribute['placeholder'] if 'placeholder' in existing_attribute else None

        fyle_attribute = fyle_attribute.replace('_', ' ').title()

        new_placeholder = None

        # Here is the explanation of what's happening in the if-else ladder below   
        # source_field is the field that's save in mapping settings, this field user may or may not fill in the custom field form
        # placeholder is the field that's saved in the detail column of destination attributes
        # fyle_attribute is what we're constructing when both of these fields would not be available

        if not (source_placeholder or placeholder):
            # If source_placeholder and placeholder are both None, then we're creating adding a self constructed placeholder
            new_placeholder = 'Select {0}'.format(fyle_attribute)
        elif not source_placeholder and placeholder:
            # If source_placeholder is None but placeholder is not, then we're choosing same place holder as 1 in detail section
            new_placeholder = placeholder
        elif source_placeholder and not placeholder:
            # If source_placeholder is not None but placeholder is None, then we're choosing the placeholder as filled by user in form
            new_placeholder = source_placeholder
        else:
            # Else, we're choosing the placeholder as filled by user in form or None
            new_placeholder = source_placeholder

        expense_custom_field_payload = {
            'id': custom_field_id,
            'name': fyle_attribute,
            'type': 'SELECT',
            'active': True,
            'mandatory': False,
            'placeholder': new_placeholder,
            'default_value': None,
            'options': fyle_expense_custom_field_options,
            'code': None
        }

        return expense_custom_field_payload


def upload_attributes_to_fyle(
    workspace_id: int, qbo_attribute_type: str, fyle_attribute_type: str, source_placeholder: str = None):
    """
    Upload attributes to Fyle
    """
    fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

    fyle_connection = FyleConnector(
        refresh_token=fyle_credentials.refresh_token
    )

    platform = PlatformConnector(fyle_credentials)

    qbo_attributes: List[DestinationAttribute] = DestinationAttribute.objects.filter(
        workspace_id=workspace_id, attribute_type=qbo_attribute_type
    )

    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_custom_field_payload = create_fyle_expense_custom_field_payload(
        qbo_attributes=qbo_attributes,
        workspace_id=workspace_id,
        fyle_attribute=fyle_attribute_type,
        source_placeholder=source_placeholder
    )

    if fyle_custom_field_payload:
        fyle_connection.connection.ExpensesCustomFields.post(fyle_custom_field_payload)
        platform.expense_custom_fields.sync()

    return qbo_attributes


def auto_create_expense_fields_mappings(
    workspace_id: int, qbo_attribute_type: str, fyle_attribute_type: str, source_placeholder: str = None
):
    """
    Create Fyle Attributes Mappings
    :return: mappings
    """
    try:
        fyle_attributes = upload_attributes_to_fyle(
            workspace_id, qbo_attribute_type, fyle_attribute_type, source_placeholder
        )
        if fyle_attributes:
            Mapping.bulk_create_mappings(fyle_attributes, fyle_attribute_type, qbo_attribute_type, workspace_id)

    except WrongParamsError as exception:
        logger.error(
            'Error while creating %s workspace_id - %s in Fyle %s %s',
            fyle_attribute_type, workspace_id, exception.message, {'error': exception.response}
        )
    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.exception(
            'Error while creating %s workspace_id - %s error: %s', fyle_attribute_type, workspace_id, error
        )


def async_auto_create_custom_field_mappings(workspace_id):
    mapping_settings = MappingSetting.objects.filter(
        is_custom=True,
        import_to_fyle=True,
        workspace_id=workspace_id
    ).all()

    if mapping_settings:
        for mapping_setting in mapping_settings:
            if mapping_setting.import_to_fyle:
                sync_qbo_attribute(mapping_setting.destination_field, workspace_id)
                auto_create_expense_fields_mappings(
                    workspace_id, mapping_setting.destination_field, mapping_setting.source_field,
                    mapping_setting.source_placeholder
                )


def schedule_fyle_attributes_creation(workspace_id: int):
    mapping_settings = MappingSetting.objects.filter(
        is_custom=True, import_to_fyle=True, workspace_id=workspace_id
    ).all()
    if mapping_settings:
        schedule, _ = Schedule.objects.get_or_create(
            func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
            args='{0}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now() + timedelta(hours=24)
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
            args='{0}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def create_fyle_merchants_payload(vendors, existing_merchants_name):
    payload: List[str] = []
    for vendor in vendors:
        if vendor.value not in existing_merchants_name:
            payload.append(vendor.value)

    return payload

def post_merchants(platform_connection: PlatformConnector, workspace_id: int, first_run: bool):
    existing_merchants_name = ExpenseAttribute.objects.filter(
        attribute_type='MERCHANT', workspace_id=workspace_id).values_list('value', flat=True)

    if first_run:
        qbo_attributes = DestinationAttribute.objects.filter(
            attribute_type='VENDOR', workspace_id=workspace_id).order_by('value', 'id')
    else:
        merchant = platform_connection.merchants.get()
        merchant_updated_at = parser.isoparse(merchant['updated_at']).strftime('%Y-%m-%d %H:%M:%S.%f')
        today_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        qbo_attributes = DestinationAttribute.objects.filter(attribute_type='VENDOR', workspace_id=workspace_id,
            updated_at__range=[merchant_updated_at, today_date]).order_by('value', 'id')

    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_payload: List[str] = create_fyle_merchants_payload(
        qbo_attributes, existing_merchants_name)

    if fyle_payload:
        platform_connection.merchants.post(fyle_payload)
        platform_connection.merchants.sync(workspace_id)

def auto_create_vendors_as_merchants(workspace_id):
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

        fyle_connection = PlatformConnector(fyle_credentials)

        existing_merchants_name = ExpenseAttribute.objects.filter(attribute_type='MERCHANT', workspace_id=workspace_id)
        first_run = False if existing_merchants_name else True

        fyle_connection.merchants.sync(workspace_id)

        sync_qbo_attribute('VENDOR', workspace_id)
        post_merchants(fyle_connection, workspace_id, first_run)

    except WrongParamsError as exception:
        logger.error(
            'Error while posting vendors as merchants to fyle for workspace_id - %s in Fyle %s %s',
            workspace_id, exception.message, {'error': exception.response}
        )

    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.exception(
            'Error while posting vendors as merchants to fyle for workspace_id - %s error: %s',
            workspace_id, error)

def schedule_vendors_as_merchants_creation(import_vendors_as_merchants, workspace_id):
    if import_vendors_as_merchants:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_vendors_as_merchants',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_vendors_as_merchants',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()
