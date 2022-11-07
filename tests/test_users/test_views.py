from django.urls import reverse
import pytest

from tests.test_fyle.fixtures import data as fyle_data

#  Will use paramaterize decorator of python later
@pytest.mark.django_db(databases=['default'])
def test_get_profile_view(api_client, test_connection):
    
    url = reverse('profile')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db(databases=['default'])
def test_get_fyle_orgs_view(api_client, test_connection, mocker):
    mocker.patch(
        'apps.users.views.get_fyle_orgs',
        return_value=fyle_data['get_all_orgs']
    )
    url = reverse('orgs')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200
