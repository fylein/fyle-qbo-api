from fyle_qbo_api.tests import settings
import pytest
import json
from django.urls import reverse
from tests.helper import dict_compare_keys
from apps.workspaces.models import FyleCredential, WorkspaceSchedule
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from .fixtures import data

def test_errors(api_client, test_connection):

    url = '/api/v2/workspaces/3/errors/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(
        url,
        data['errors_true'],
    )

    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response[0], data['response'][0]) == [], 'workspaces api returns a diff in the keys'

    response = api_client.get(
        url,
        data['errors_false'],
    )

    assert response.status_code == 200

    response = json.loads(response.content)

    assert response == []