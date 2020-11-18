import logging
import traceback
from datetime import datetime

from typing import List, Dict

from django_q.models import Schedule

from apps.fyle.utils import FyleConnector
from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import QBOCredential, FyleCredential
from fyle_accounting_mappings.models import MappingSetting, Mapping, DestinationAttribute
from fylesdk import WrongParamsError

logger = logging.getLogger(__name__)


def create_fyle_projects_payload(projects: List[DestinationAttribute]):
    """
    Create Fyle Projects Payload from QBO Customer / Projects
    :param projects: QBO Projects
    :return: Fyle Projects Payload
    """
    payload = []

    for project in projects:
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

    qbo_attributes: List[DestinationAttribute] = qbo_connection.sync_customers()

    fyle_payload: List[Dict] = create_fyle_projects_payload(qbo_attributes)

    fyle_projects = fyle_connection.connection.Projects.post(fyle_payload)
    fyle_connection.sync_projects(fyle_projects)
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
            mapping = Mapping.create_or_update_mapping(
                source_type='PROJECT',
                destination_type='CUSTOMER',
                source_value=project.value,
                destination_value=project.value,
                workspace_id=workspace_id
            )
            project_mappings.append(mapping)

        return project_mappings
    except WrongParamsError as exception:
        logger.exception(
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
