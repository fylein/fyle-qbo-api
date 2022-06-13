from apps.mappings.models import GeneralMapping
from apps.workspaces.models import WorkspaceGeneralSettings

def test_get_queryset(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/tasks/all/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url, {
        'expense_group_ids': '9',
        'task_type': 'CREATING_EXPENSE',
        'status': 'COMPLETE'
    })
    assert response.status_code==200


def test_get_task_by_id(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/tasks/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url, {
        'id': '8'
    })
    assert response.status_code==200


def test_get_task_by_expense_group_id(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/tasks/expense_group/9/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code==200
    