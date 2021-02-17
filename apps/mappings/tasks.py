import logging
import traceback
from datetime import datetime, timedelta

from typing import List, Dict

from django.db.models import Q
from django_q.models import Schedule

from apps.fyle.utils import FyleConnector
from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import QBOCredential, FyleCredential
from fyle_accounting_mappings.models import MappingSetting, Mapping, DestinationAttribute, ExpenseAttribute
from fylesdk import WrongParamsError

logger = logging.getLogger(__name__)


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

    qbo_attributes: List[DestinationAttribute] = qbo_connection.sync_customers()

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

    fyle_projects = upload_projects_to_fyle(workspace_id=workspace_id)

    project_mappings = []

    try:
        for project in fyle_projects:
            try:
                mapping = Mapping.create_or_update_mapping(
                    source_type='PROJECT',
                    destination_type='CUSTOMER',
                    source_value=project.value,
                    destination_value=project.value,
                    destination_id=project.destination_id,
                    workspace_id=workspace_id
                )
                project_mappings.append(mapping)
            except ExpenseAttribute.DoesNotExist:
                detail = {
                    'source_value': project.value,
                    'destination_value': project.value
                }
                logger.error(
                    'Error while creating categories auto mapping workspace_id - %s %s',
                    workspace_id, {'payload': detail}
                )
                raise ExpenseAttribute.DoesNotExist

        return project_mappings

    except ExpenseAttribute.DoesNotExist as exception:
        detail = {
            'source_value': project.value,
            'destination_value': project.value
        }
        logger.error(
            'Error while creating projects auto mapping workspace_id - %s %s',
            workspace_id, {'payload': detail}
        )

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
    qbo_attributes: List[DestinationAttribute] = qbo_connection.sync_accounts(account_type='Expense')

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
    MappingSetting.bulk_upsert_mapping_setting([{
        'source_field': 'CATEGORY',
        'destination_field': 'ACCOUNT'
    }], workspace_id=workspace_id)

    fyle_categories = upload_categories_to_fyle(workspace_id=workspace_id)

    category_mappings = []

    try:
        for category in fyle_categories:
            try:
                mapping = Mapping.create_or_update_mapping(
                    source_type='CATEGORY',
                    destination_type='ACCOUNT',
                    source_value=category.value,
                    destination_value=category.value,
                    destination_id=category.destination_id,
                    workspace_id=workspace_id
                )
                category_mappings.append(mapping)

            except ExpenseAttribute.DoesNotExist:
                detail = {
                    'source_value': category.value,
                    'destination_value': category.value
                }
                logger.error(
                    'Error while creating categories auto mapping workspace_id - %s %s',
                    workspace_id, {'payload': detail}
                )
                raise ExpenseAttribute.DoesNotExist

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


def filter_expense_attributes(workspace_id: str, **filters):
    return ExpenseAttribute.objects.filter(attribute_type='EMPLOYEE', workspace_id=workspace_id, **filters).all()


def auto_create_employee_mappings(source_attributes: List[ExpenseAttribute], mapping_attributes: dict):
    for source in source_attributes:
        mapping = Mapping.objects.filter(
            source_type='EMPLOYEE',
            destination_type=mapping_attributes['destination_type'],
            source__value=source.value,
            workspace_id=mapping_attributes['workspace_id']
        ).first()

        logger.error(mapping)

        if not mapping:
            Mapping.create_or_update_mapping(
                source_type='EMPLOYEE',
                destination_type=mapping_attributes['destination_type'],
                source_value=source.value,
                destination_value=mapping_attributes['destination_value'],
                destination_id=mapping_attributes['destination_id'],
                workspace_id=mapping_attributes['workspace_id']
            )

            if mapping_attributes['destination_type'] != 'CREDIT_CARD_ACCOUNT':
                source.auto_mapped = True
                source.save(update_fields=['auto_mapped'])


def construct_filters_employee_mappings(employee: DestinationAttribute, employee_mapping_preference: str):
    filters = {}
    if employee_mapping_preference == 'EMAIL':
        if employee.detail and employee.detail['email']:
            filters = {
                'value__iexact': employee.detail['email']
            }

    elif employee_mapping_preference == 'NAME':
        filters = {
            'detail__full_name__iexact': employee.value
        }

    elif employee_mapping_preference == 'EMPLOYEE_CODE':
        filters = {
            'detail__employee_code__iexact': employee.value
        }

    return filters


def async_auto_map_employees(employee_mapping_preference: str, workspace_id: str):
    mapping_setting = MappingSetting.objects.filter(
        ~Q(destination_field='CREDIT_CARD_ACCOUNT'),
        source_field='EMPLOYEE', workspace_id=workspace_id
    ).first()

    destination_type = None
    if mapping_setting:
        destination_type = mapping_setting.destination_field

    source_attributes = []
    employee_attributes = DestinationAttribute.objects.filter(attribute_type=destination_type,
                                                              workspace_id=workspace_id)

    for employee in employee_attributes:
        filters = construct_filters_employee_mappings(employee, employee_mapping_preference)

        if filters:
            filters['auto_mapped'] = False
            source_attributes = filter_expense_attributes(workspace_id, **filters)

        mapping_attributes = {
            'destination_type': destination_type,
            'destination_value': employee.value,
            'destination_id': employee.destination_id,
            'workspace_id': workspace_id
        }

        auto_create_employee_mappings(source_attributes, mapping_attributes)


def schedule_auto_map_employees(employee_mapping_preference: str, workspace_id: str):
    Schedule.objects.create(
        func='apps.mappings.tasks.async_auto_map_employees',
        args='"{0}", {1}'.format(employee_mapping_preference, workspace_id),
        schedule_type=Schedule.ONCE,
        next_run=datetime.now() + timedelta(minutes=5)
    )


def async_auto_map_ccc_account(default_ccc_account_name: str, default_ccc_account_id: str, workspace_id: str):
    source_attributes = filter_expense_attributes(workspace_id)

    logger.error(source_attributes)

    mapping_attributes = {
        'destination_type': 'CREDIT_CARD_ACCOUNT',
        'destination_value': default_ccc_account_name,
        'destination_id': default_ccc_account_id,
        'workspace_id': workspace_id
    }

    auto_create_employee_mappings(source_attributes, mapping_attributes)


def schedule_auto_map_ccc_employees(default_ccc_account_name: str, default_ccc_account_id: str, workspace_id: str):
    Schedule.objects.create(
        func='apps.mappings.tasks.async_auto_map_ccc_account',
        args='"{0}", "{1}", {2}'.format(default_ccc_account_name, default_ccc_account_id, workspace_id),
        schedule_type=Schedule.ONCE,
        next_run=datetime.now() + timedelta(minutes=5)
    )
