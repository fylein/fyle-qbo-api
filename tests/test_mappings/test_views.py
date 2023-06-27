from pkg_resources import working_set
import pytest
import json
from django.urls import reverse

from apps.mappings.models import GeneralMapping
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.workspaces.models import Workspace
from .fixtures import data


def test_auto_map_employee(api_client, test_connection):
    url = "/api/workspaces/3/mappings/auto_map_employees/trigger/"

    api_client.credentials(
        HTTP_AUTHORIZATION="Bearer {}".format(test_connection.access_token)
    )

    response = api_client.post(url)
    assert response.status_code == 200

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    general_settings.auto_map_employees = None
    general_settings.save()

    response = api_client.post(url)
    assert response.status_code == 400

    general_mapping = GeneralMapping.objects.get(workspace_id=3)
    general_mapping.delete()

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    general_settings.auto_map_employees = "EMAIL"
    general_settings.save()

    response = api_client.post(url)
    assert response.status_code == 400
