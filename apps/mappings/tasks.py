import logging
import traceback
from datetime import datetime, timedelta

from typing import List, Dict

from django_q.models import Schedule

from fyle_accounting_mappings.models import MappingSetting, Mapping, DestinationAttribute, ExpenseAttribute
from fylesdk import WrongParamsError

from apps.fyle.utils import FyleConnector
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import QBOCredential, FyleCredential, WorkspaceGeneralSettings

from .constants import FYLE_EXPENSE_SYSTEM_FIELDS

logger = logging.getLogger(__name__)


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
                'active': True if project.active is None else project.active
            })

    return payload


def post_projects_in_batches(fyle_connection: FyleConnector, workspace_id: int, destination_field: str):
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
            fyle_connection.connection.Projects.post(fyle_payload)
            fyle_connection.sync_projects()

        Mapping.bulk_create_mappings(paginated_qbo_attributes, 'PROJECT', destination_field, workspace_id)


def auto_create_project_mappings(workspace_id: int):
    """
    Create Project Mappings
    :return: mappings
    """
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

        fyle_connection = FyleConnector(
            refresh_token=fyle_credentials.refresh_token,
            workspace_id=workspace_id
        )

        fyle_connection.sync_projects()

        mapping_setting = MappingSetting.objects.get(
            source_field='PROJECT', workspace_id=workspace_id
        )

        sync_qbo_attribute(mapping_setting.destination_field, workspace_id)

        post_projects_in_batches(fyle_connection, workspace_id, mapping_setting.destination_field)

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
        logger.error(
            'Error while creating projects workspace_id - %s error: %s',
            workspace_id, error
        )


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
                'enabled': category.active
            })

    return payload


def upload_categories_to_fyle(workspace_id):
    """
    Upload categories to Fyle
    """
    fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)
    qbo_credentials: QBOCredential = QBOCredential.objects.get(workspace_id=workspace_id)

    fyle_connection = FyleConnector(
        refresh_token=fyle_credentials.refresh_token,
        workspace_id=workspace_id
    )

    qbo_connection = QBOConnector(
        credentials_object=qbo_credentials,
        workspace_id=workspace_id
    )
    fyle_connection.sync_categories(False)
    qbo_connection.sync_accounts()
    qbo_attributes: List[DestinationAttribute] = DestinationAttribute.objects.filter(
        workspace_id=workspace_id, attribute_type='ACCOUNT').all()
    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_payload: List[Dict] = create_fyle_categories_payload(qbo_attributes, workspace_id)

    if fyle_payload:
        fyle_connection.connection.Categories.post(fyle_payload)
        fyle_connection.sync_categories(False)

    return qbo_attributes


def auto_create_category_mappings(workspace_id):
    """
    Create Category Mappings
    :return: mappings
    """
    try:
        fyle_categories = upload_categories_to_fyle(workspace_id=workspace_id)
        category_mappings = Mapping.bulk_create_mappings(fyle_categories, 'CATEGORY', 'ACCOUNT', workspace_id)
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
        logger.error(
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


def async_auto_map_employees(workspace_id: int):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    employee_mapping_preference = general_settings.auto_map_employees
    destination_type = general_settings.employee_field_mapping

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_connection = FyleConnector(refresh_token=fyle_credentials.refresh_token, workspace_id=workspace_id)

    qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    fyle_connection.sync_employees()
    if destination_type == 'EMPLOYEE':
        qbo_connection.sync_employees()
    else:
        qbo_connection.sync_vendors()

    Mapping.auto_map_employees(destination_type, employee_mapping_preference, workspace_id)


def schedule_auto_map_employees(employee_mapping_preference: str, workspace_id: str):
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


def async_auto_map_ccc_account(workspace_id: str):
    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    if general_mappings:
        default_ccc_account_id = general_mappings.default_ccc_account_id

        if default_ccc_account_id:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            fyle_connection = FyleConnector(refresh_token=fyle_credentials.refresh_token, workspace_id=workspace_id)
            fyle_connection.sync_employees()

            Mapping.auto_map_ccc_employees('CREDIT_CARD_ACCOUNT', default_ccc_account_id, workspace_id)


def schedule_auto_map_ccc_employees(workspace_id: str):
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


def sync_qbo_attribute(qbo_attribute_type: str, workspace_id: int):
    qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    if qbo_attribute_type == 'CUSTOMER':
        qbo_connection.sync_customers()

    elif qbo_attribute_type == 'DEPARTMENT':
        qbo_connection.sync_departments()

    elif qbo_attribute_type == 'CLASS':
        qbo_connection.sync_classes()


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
                'enabled': True if qbo_attribute.active is None else qbo_attribute.active,
                'description': 'Cost Center - {0}, Id - {1}'.format(
                    qbo_attribute.value,
                    qbo_attribute.destination_id
                )
            })

    return fyle_cost_centers_payload


def post_cost_centers_in_batches(fyle_connection: FyleConnector, workspace_id: int, qbo_attribute_type: str):
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
            fyle_connection.connection.CostCenters.post(fyle_payload)
            fyle_connection.sync_cost_centers()

        Mapping.bulk_create_mappings(paginated_qbo_attributes, 'COST_CENTER', qbo_attribute_type, workspace_id)


def auto_create_cost_center_mappings(workspace_id):
    """
    Create Cost Center Mappings
    """
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

        fyle_connection = FyleConnector(
            refresh_token=fyle_credentials.refresh_token,
            workspace_id=workspace_id
        )

        mapping_setting = MappingSetting.objects.get(
            source_field='COST_CENTER', import_to_fyle=True, workspace_id=workspace_id
        )

        fyle_connection.sync_cost_centers()

        sync_qbo_attribute(mapping_setting.destination_field, workspace_id)

        post_cost_centers_in_batches(fyle_connection, workspace_id, mapping_setting.destination_field)

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
        logger.error(
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


def create_fyle_expense_custom_field_payload(qbo_attributes: List[DestinationAttribute], workspace_id: int,
                                             fyle_attribute: str):
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
        if existing_attribute is not None:
            custom_field_id = existing_attribute['custom_field_id']

        fyle_attribute = fyle_attribute.replace('_', ' ').title()

        expense_custom_field_payload = {
            'id': custom_field_id,
            'name': fyle_attribute,
            'type': 'SELECT',
            'active': True,
            'mandatory': False,
            'placeholder': 'Select {0}'.format(fyle_attribute),
            'default_value': None,
            'options': fyle_expense_custom_field_options,
            'code': None
        }

        return expense_custom_field_payload


def upload_attributes_to_fyle(workspace_id: int, qbo_attribute_type: str, fyle_attribute_type: str):
    """
    Upload attributes to Fyle
    """
    fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

    fyle_connection = FyleConnector(refresh_token=fyle_credentials.refresh_token, workspace_id=workspace_id)

    qbo_attributes: List[DestinationAttribute] = DestinationAttribute.objects.filter(
        workspace_id=workspace_id, attribute_type=qbo_attribute_type
    )

    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_custom_field_payload = create_fyle_expense_custom_field_payload(
        qbo_attributes=qbo_attributes,
        workspace_id=workspace_id,
        fyle_attribute=fyle_attribute_type
    )

    if fyle_custom_field_payload:
        fyle_connection.connection.ExpensesCustomFields.post(fyle_custom_field_payload)
        fyle_connection.sync_expense_custom_fields(active_only=True)

    return qbo_attributes


def auto_create_expense_fields_mappings(workspace_id: int, qbo_attribute_type: str, fyle_attribute_type: str):
    """
    Create Fyle Attributes Mappings
    :return: mappings
    """
    try:
        fyle_attributes = upload_attributes_to_fyle(workspace_id, qbo_attribute_type, fyle_attribute_type)
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
        logger.error(
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
                    workspace_id, mapping_setting.destination_field, mapping_setting.source_field
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
