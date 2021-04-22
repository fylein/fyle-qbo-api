import logging
import traceback
from datetime import datetime
from time import time

from typing import List, Dict

from django.db.models import Q
from django_q.models import Schedule

from apps.fyle.utils import FyleConnector
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import QBOCredential, FyleCredential, WorkspaceGeneralSettings
from fyle_accounting_mappings.models import MappingSetting, Mapping, DestinationAttribute, ExpenseAttribute
from fylesdk import WrongParamsError

logger = logging.getLogger(__name__)


def remove_duplicates(ns_attributes: List[DestinationAttribute]):
    unique_attributes = []

    attribute_values = []

    for attribute in ns_attributes:
        if attribute.value not in attribute_values:
            unique_attributes.append(attribute)
            attribute_values.append(attribute.value)

    return unique_attributes


def create_fyle_projects_payload(projects: List[DestinationAttribute], workspace_id: int):
    """
    Create Fyle Projects Payload from QBO Customer / Projects
    :param workspace_id: integer id of workspace
    :param projects: QBO Projects
    :return: Fyle Projects Payload
    """
    payload = []

    existing_project_names = ExpenseAttribute.objects.filter(
        attribute_type='PROJECT', workspace_id=workspace_id).values_list('value', flat=True)

    for project in projects:
        if project.value not in existing_project_names:
            payload.append({
                'name': project.value,
                'code': project.destination_id,
                'description': 'Quickbooks Online Customer / Project - {0}, Id - {1}'.format(
                    project.value,
                    project.destination_id
                ),
                'active': True if project.active is None else project.active
            })

    return payload


def upload_projects_to_fyle(workspace_id):
    """
    Upload projects to Fyle
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

    fyle_connection.sync_projects()

    qbo_connection.sync_customers()
    qbo_attributes: List[DestinationAttribute] = DestinationAttribute.objects.filter(
        workspace_id=workspace_id, attribute_type='CUSTOMER').all()
    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_payload: List[Dict] = create_fyle_projects_payload(qbo_attributes, workspace_id)

    if fyle_payload:
        fyle_connection.connection.Projects.post(fyle_payload)
        fyle_connection.sync_projects()

    return qbo_attributes


def auto_create_project_mappings(workspace_id):
    """
    Create Project Mappings
    :return: mappings
    """
    MappingSetting.bulk_upsert_mapping_setting([{
        'source_field': 'PROJECT',
        'destination_field': 'CUSTOMER'
    }], workspace_id=workspace_id)

    try:
        fyle_projects = upload_projects_to_fyle(workspace_id=workspace_id)
        project_mappings = Mapping.bulk_create_mappings(fyle_projects, 'PROJECT', 'CUSTOMER', workspace_id)
        return project_mappings

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


def schedule_projects_creation(import_projects, workspace_id):
    if import_projects:
        start_datetime = datetime.now()
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_project_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 6 * 60,
                'next_run': start_datetime
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
    qbo_connection.sync_accounts(account_type='Expense')
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

    mapping_setting = MappingSetting.objects.filter(
        ~Q(destination_field='CREDIT_CARD_ACCOUNT'),
        source_field='EMPLOYEE', workspace_id=workspace_id
    ).first()
    destination_type = mapping_setting.destination_field

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_connection = FyleConnector(refresh_token=fyle_credentials.refresh_token, workspace_id=workspace_id)

    qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    fyle_connection.sync_employees()
    if destination_type == 'EMPLOYEE':
        qbo_connection.sync_employees()
    else:
        qbo_connection.sync_vendors()

    Mapping.auto_map_employees('EMPLOYEE', destination_type, employee_mapping_preference, workspace_id)


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
    general_mappings = GeneralMapping.objects.get(workspace_id=workspace_id)
    default_ccc_account_id = general_mappings.default_ccc_account_id

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_connection = FyleConnector(refresh_token=fyle_credentials.refresh_token, workspace_id=workspace_id)
    fyle_connection.sync_employees()

    Mapping.auto_map_ccc_employees('EMPLOYEE', 'CREDIT_CARD_ACCOUNT', default_ccc_account_id, workspace_id)


def schedule_auto_map_ccc_employees(workspace_id: str):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    if general_settings.auto_map_employees and general_settings.corporate_credit_card_expenses_object:
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
