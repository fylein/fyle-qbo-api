from django.urls import reverse
import pytest

#  Will use paramaterize decorator of python later
def test_get_profile_view(api_client, test_connection):
    
    access_token = test_connection.access_token
    url = reverse('profile')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

def test_get_fyle_orgs_view(api_client, test_connection):
    
    access_token = test_connection.access_token
    url = reverse('orgs')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
