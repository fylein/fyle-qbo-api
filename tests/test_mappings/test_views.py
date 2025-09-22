def test_auto_map_employee(mocker, api_client, test_connection):

    url = '/api/workspaces/3/mappings/auto_map_employees/trigger/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    mock_publish_to_rabbitmq = mocker.patch('apps.mappings.views.publish_to_rabbitmq')

    response = api_client.post(url)
    assert response.status_code == 200

    assert mock_publish_to_rabbitmq.call_count == 1
