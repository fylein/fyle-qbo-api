import logging
from typing import Dict, List

from django_q.tasks import Chain
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping, ExpenseAttribute, Mapping, MappingSetting
from fyle_integrations_platform_connector import PlatformConnector

from apps.mappings.exceptions import handle_import_exceptions
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.utils import QBOConnector
from apps.tasks.models import Error
from apps.workspaces.models import FyleCredential, QBOCredential, WorkspaceGeneralSettings

logger = logging.getLogger(__name__)
logger.level = logging.INFO

DEFAULT_FYLE_CATEGORIES = [
    'train',
    'fuel',
    'office supplies',
    'utility',
    'entertainment',
    'others',
    'mileage',
    'food',
    'per diem',
    'bus',
    'taxi',
    'mail',
    'lodging',
    'professional services',
    'airlines',
    'software',
    'parking',
    'unspecified',
    'rental',
    'groceries',
]


def resolve_expense_attribute_errors(source_attribute_type: str, workspace_id: int, destination_attribute_type: str = None):
    """
    Resolve Expense Attribute Errors
    :return: None
    """
    errored_attribute_ids: List[int] = Error.objects.filter(is_resolved=False, workspace_id=workspace_id, type='{}_MAPPING'.format(source_attribute_type)).values_list('expense_attribute_id', flat=True)

    if errored_attribute_ids:
        mapped_attribute_ids = []

        if source_attribute_type in ('TAX_GROUP'):
            mapped_attribute_ids: List[int] = Mapping.objects.filter(source_id__in=errored_attribute_ids).values_list('source_id', flat=True)

        elif source_attribute_type == 'EMPLOYEE':
            if destination_attribute_type == 'EMPLOYEE':
                params = {'source_employee_id__in': errored_attribute_ids, 'destination_employee_id__isnull': False}
            else:
                params = {'source_employee_id__in': errored_attribute_ids, 'destination_vendor_id__isnull': False}
            mapped_attribute_ids: List[int] = EmployeeMapping.objects.filter(**params).values_list('source_employee_id', flat=True)

        if mapped_attribute_ids:
            Error.objects.filter(expense_attribute_id__in=mapped_attribute_ids).update(is_resolved=True)


def remove_duplicates(qbo_attributes: List[DestinationAttribute]):
    unique_attributes = []

    attribute_values = []

    for attribute in qbo_attributes:
        if attribute.value.lower() not in attribute_values:
            unique_attributes.append(attribute)
            attribute_values.append(attribute.value.lower())

    return unique_attributes


@handle_import_exceptions(task_name='Auto Create Tax Code Mappings')
def auto_create_tax_codes_mappings(workspace_id: int):
    """
    Create Tax Codes Mappings
    :return: None
    """

    fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

    platform = PlatformConnector(fyle_credentials)

    platform.tax_groups.sync()

    mapping_setting = MappingSetting.objects.get(source_field='TAX_GROUP', workspace_id=workspace_id)

    sync_qbo_attribute(mapping_setting.destination_field, workspace_id)
    upload_tax_groups_to_fyle(platform, workspace_id)


def get_existing_source_and_mappings(destination_type: str, workspace_id: int):
    existing_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).all()

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


def check_exact_matches(employee_mapping_preference: str, source_attribute: ExpenseAttribute, destination_id_value_map: dict, destination_type: str):
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
    elif source_attribute.detail and employee_mapping_preference == 'NAME':
        source_value = source_attribute.detail['full_name']
    elif source_attribute.detail and employee_mapping_preference == 'EMPLOYEE_CODE':
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


def construct_mapping_payload(employee_source_attributes: List[ExpenseAttribute], employee_mapping_preference: str, destination_id_value_map: dict, destination_type: str, workspace_id: int):
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
            destination = check_exact_matches(employee_mapping_preference, source_attribute, destination_id_value_map, destination_type)
            if destination:
                update_key = list(destination.keys())[0]
                if source_attribute.id in existing_mappings_map:
                    # If employee mapping row exists, then update it
                    mapping_updation_batch.append(EmployeeMapping(id=existing_mappings_map[source_attribute.id], source_employee=source_attribute, **destination))
                else:
                    # If employee mapping row does not exist, then create it
                    mapping_creation_batch.append(EmployeeMapping(source_employee_id=source_attribute.id, workspace_id=workspace_id, **destination))

    return mapping_creation_batch, mapping_updation_batch, update_key


def create_mappings_and_update_flag(mapping_creation_batch: List[EmployeeMapping], mapping_updation_batch: List[EmployeeMapping], update_key: str):
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
        EmployeeMapping.objects.bulk_update(mapping_updation_batch, fields=[update_key], batch_size=50)
        for mapping in mapping_updation_batch:
            mappings.append(mapping)

    expense_attributes_to_be_updated = []

    for mapping in mappings:
        expense_attributes_to_be_updated.append(ExpenseAttribute(id=mapping.source_employee.id, auto_mapped=True))

    if expense_attributes_to_be_updated:
        ExpenseAttribute.objects.bulk_update(expense_attributes_to_be_updated, fields=['auto_mapped'], batch_size=50)

    return mappings


def auto_map_employees(destination_type: str, employee_mapping_preference: str, workspace_id: int):
    """
    Auto map employees
    :param destination_type: Destination Type of mappings
    :param employee_mapping_preference: Employee Mapping Preference
    :param workspace_id: Workspace ID
    """
    # Filtering only not mapped destination attributes
    employee_destination_attributes = DestinationAttribute.objects.filter(attribute_type=destination_type, workspace_id=workspace_id).all()

    destination_id_value_map = {}
    for destination_employee in employee_destination_attributes:
        value_to_be_appended = None
        if employee_mapping_preference == 'EMAIL' and destination_employee.detail and destination_employee.detail['email']:
            value_to_be_appended = destination_employee.detail['email'].replace('*', '')
        elif employee_mapping_preference in ['NAME', 'EMPLOYEE_CODE']:
            value_to_be_appended = destination_employee.value.replace('*', '')

        if value_to_be_appended:
            destination_id_value_map[value_to_be_appended.lower()] = destination_employee.id

    filters = {'attribute_type': 'EMPLOYEE', 'workspace_id': workspace_id}

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

    mapping_creation_batch, mapping_updation_batch, update_key = construct_mapping_payload(employee_source_attributes, employee_mapping_preference, destination_id_value_map, destination_type, workspace_id)

    create_mappings_and_update_flag(mapping_creation_batch, mapping_updation_batch, update_key)


@handle_import_exceptions(task_name='Async Auto Map Employees')
def async_auto_map_employees(workspace_id: int):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    employee_mapping_preference = general_settings.auto_map_employees
    destination_type = general_settings.employee_field_mapping

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    platform.employees.sync()
    if destination_type == 'EMPLOYEE':
        qbo_connection.sync_employees()
    else:
        qbo_connection.sync_vendors()

    auto_map_employees(destination_type, employee_mapping_preference, workspace_id)

    resolve_expense_attribute_errors(source_attribute_type='EMPLOYEE', workspace_id=workspace_id, destination_attribute_type=destination_type)


def auto_map_ccc_employees(default_ccc_account_id: str, workspace_id: int):
    """
    Auto map ccc employees
    :param default_ccc_account_id: Default CCC Account ID
    :param workspace_id: Workspace ID
    """
    employee_source_attributes = ExpenseAttribute.objects.filter(attribute_type='EMPLOYEE', workspace_id=workspace_id).all()

    default_destination_attribute = DestinationAttribute.objects.filter(destination_id=default_ccc_account_id, workspace_id=workspace_id, attribute_type='CREDIT_CARD_ACCOUNT').first()

    existing_source_ids, existing_mappings = get_existing_source_and_mappings('CREDIT_CARD_ACCOUNT', workspace_id)
    existing_mappings_map = {mapping.source_employee_id: mapping.id for mapping in existing_mappings}

    mapping_creation_batch = []
    mapping_updation_batch = []
    for source_employee in employee_source_attributes:
        # Ignoring already present mappings
        if source_employee.id not in existing_source_ids:
            if source_employee.id in existing_mappings_map:
                # If employee mapping row exists, then update it
                mapping_updation_batch.append(EmployeeMapping(id=existing_mappings_map[source_employee.id], destination_card_account_id=default_destination_attribute.id))
            else:
                # If employee mapping row does not exist, then create it
                mapping_creation_batch.append(EmployeeMapping(source_employee_id=source_employee.id, destination_card_account_id=default_destination_attribute.id, workspace_id=workspace_id))

    if mapping_creation_batch:
        EmployeeMapping.objects.bulk_create(mapping_creation_batch, batch_size=50)

    if mapping_updation_batch:
        EmployeeMapping.objects.bulk_update(mapping_updation_batch, fields=['destination_card_account_id'], batch_size=50)


def async_auto_map_ccc_account(workspace_id: int):
    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    if general_mappings:
        default_ccc_account_id = general_mappings.default_ccc_account_id

        if default_ccc_account_id:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            platform = PlatformConnector(fyle_credentials)

            platform.employees.sync()

            auto_map_ccc_employees(default_ccc_account_id, workspace_id)


def upload_tax_groups_to_fyle(platform_connection: PlatformConnector, workspace_id: int):
    existing_tax_codes_name = ExpenseAttribute.objects.filter(attribute_type='TAX_GROUP', workspace_id=workspace_id).values_list('value', flat=True)

    qbo_attributes = DestinationAttribute.objects.filter(attribute_type='TAX_CODE', workspace_id=workspace_id).order_by('value', 'id')

    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_payload: List[Dict] = create_fyle_tax_group_payload(qbo_attributes, existing_tax_codes_name)

    if fyle_payload:
        platform_connection.tax_groups.post_bulk(fyle_payload)

    platform_connection.tax_groups.sync()
    Mapping.bulk_create_mappings(qbo_attributes, 'TAX_GROUP', 'TAX_CODE', workspace_id)
    resolve_expense_attribute_errors(source_attribute_type='TAX_GROUP', workspace_id=workspace_id)


def sync_qbo_attribute(qbo_attribute_type: str, workspace_id: int):
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
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
            fyle_tax_group_payload.append({'name': qbo_attribute.value, 'is_enabled': True, 'percentage': round((qbo_attribute.detail['tax_rate'] / 100), 2)})

    return fyle_tax_group_payload


def create_fyle_merchants_payload(vendors, existing_merchants_name):
    payload: List[str] = []
    for vendor in vendors:
        if vendor.value not in existing_merchants_name:
            payload.append(vendor.value)

    return payload


def post_merchants(platform_connection: PlatformConnector, workspace_id: int):
    existing_merchants_name = ExpenseAttribute.objects.filter(attribute_type='MERCHANT', workspace_id=workspace_id).values_list('value', flat=True)

    qbo_attributes = DestinationAttribute.objects.filter(attribute_type='VENDOR', active=True, workspace_id=workspace_id).order_by('value', 'id')

    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_payload: List[str] = create_fyle_merchants_payload(qbo_attributes, existing_merchants_name)

    if fyle_payload:
        platform_connection.merchants.post(fyle_payload)
        platform_connection.merchants.sync()


@handle_import_exceptions(task_name='Auto Create Vendors as Merchants')
def auto_create_vendors_as_merchants(workspace_id):
    fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

    fyle_connection = PlatformConnector(fyle_credentials)

    fyle_connection.merchants.sync()

    sync_qbo_attribute('VENDOR', workspace_id)
    post_merchants(fyle_connection, workspace_id)


def auto_import_and_map_fyle_fields(workspace_id):
    """
    Auto import and map fyle fields
    """
    workspace_general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    chain = Chain()

    if workspace_general_settings.import_vendors_as_merchants:
        chain.append('apps.mappings.tasks.auto_create_vendors_as_merchants', workspace_id)

    if chain.length() > 0:
        chain.run()
