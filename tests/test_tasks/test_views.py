from apps.mappings.models import GeneralMapping
from apps.workspaces.models import WorkspaceGeneralSettings


def test_get_queryset(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/tasks/all/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url, {
        'expense_group_id__in': '9',
        'type__in': 'CREATING_EXPENSE',
        'status__in': 'COMPLETE'
    })
    assert response.status_code==200
