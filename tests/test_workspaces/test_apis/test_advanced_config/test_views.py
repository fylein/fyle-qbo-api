import json

import pytest

from apps.workspaces.models import FyleCredential, Workspace
from tests.helper import dict_compare_keys
from tests.test_workspaces.test_apis.test_advanced_config.fixtures import data


@pytest.mark.django_db()
def test_advanced_config(api_client, test_connection, db):
    FyleCredential.objects.update_or_create(
        workspace_id=3,
        defaults={
            'refresh_token': 'ey.ey.ey',
            'cluster_domain': 'cluster_domain'
        }
    )
    workspace = Workspace.objects.get(id=3)
    workspace.onboarding_state = 'ADVANCED_CONFIGURATION'
    workspace.save()

    url = '/api/v2/workspaces/3/advanced_configurations/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.put(url, data=data['advanced_config'], format='json')

    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['response']) == [], 'workspaces api returns a diff in the keys'

    response = api_client.put(url, data={'general_mappings': {}}, format='json')

    assert response.status_code == 400

    response = api_client.put(url, data={'workspace_general_settings': {}}, format='json')

    assert response.status_code == 400

    response = api_client.put(url, data={'workspace_schedules': {}}, format='json')

    assert response.status_code == 400
