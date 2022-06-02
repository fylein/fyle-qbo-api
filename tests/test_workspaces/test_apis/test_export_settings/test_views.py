from fyle_qbo_api.tests import settings
import pytest
import json
from django.urls import reverse
from tests.helper import dict_compare_keys
from apps.workspaces.models import FyleCredential, WorkspaceSchedule
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from .fixtures import data

def test_export_settings(api_client, test_connection):

    workspace = Workspace.objects.get(id=3)
    workspace.onboarding_state = 'EXPORT_SETTINGS'
    workspace.save()

    workspace_general_settings_instance = WorkspaceGeneralSettings.objects.filter(workspace_id=3).first() 
    workspace_general_settings_instance.map_merchant_to_vendor = True
    workspace_general_settings_instance.category_sync_version = 'v2'
    workspace_general_settings_instance.save()

    url = '/api/v2/workspaces/3/export_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.put(
        url,
        data=data['export_settings'],
        format='json'
    )

    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['response']) == [], 'workspaces api returns a diff in the keys'

    response = api_client.put(
        url,
        data=data['export_settings_missing_values'],
        format='json'
    )

    assert response.status_code == 400
