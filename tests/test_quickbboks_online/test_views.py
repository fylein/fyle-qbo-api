from os import access
from django.urls import reverse
import pytest
import json

#  Will use paramaterize decorator of python later
@pytest.mark.django_db(databases=['default'])
def test_quickbooks_fields_view(api_client, test_connection):

   access_token = test_connection.access_token
   url = reverse('quickbooks-fields', 
      kwargs={
            'workspace_id': 8
         }
      )

   api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

   response = api_client.get(url)
   assert response.status_code == 200
   response = json.loads(response.content)

   assert len(response) == 3

@pytest.mark.django_db(databases=['default'])
def test_destination_attributes_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = reverse('destination-attributes', 
        kwargs={
                'workspace_id': 8
            }
        )

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url,{
        'attribute_types':'CUSTOMER'
    })
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 34
