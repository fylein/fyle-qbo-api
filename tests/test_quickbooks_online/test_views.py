import base64
import hashlib
import hmac
import json
from unittest import mock
from unittest.mock import patch

import pytest
from django.test import override_settings
from django.urls import resolve, reverse
from fyle_accounting_mappings.models import DestinationAttribute
from rest_framework import status

from apps.quickbooks_online.models import QBOWebhookIncoming
from apps.workspaces.models import QBOCredential
from tests.test_quickbooks_online.fixtures import data


def test_destination_attributes_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = reverse('destination-attributes', kwargs={'workspace_id': 3})

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url, {'attribute_type__in': 'ACCOUNT', 'display_name__in': 'Account', 'active': True})
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 63


def test_searched_destination_attributes_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = reverse('searching-destination-attributes', kwargs={'workspace_id': 3})

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url, {'attribute_type': 'ACCOUNT', 'display_name': 'Account', 'limit': 30})
    assert response.status_code == 200
    response = json.loads(response.content)
    assert len(response['results']) == 30


def test_qbo_attributes_view(api_client, test_connection):

    access_token = test_connection.access_token
    url = reverse('qbo-attributes', kwargs={'workspace_id': 3})

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url, {'attribute_type__in': 'CUSTOMER'})
    assert response.status_code == 200
    response = json.loads(response.content)

    assert len(response) == 1


def test_vendor_view(mocker, api_client, test_connection):
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.sync_vendors', return_value=None)

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/vendors/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url, {'attribute_type__in': 'VENDOR', 'limit': 10})
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response['results']) == 10

    vendor = DestinationAttribute.objects.filter(attribute_type='VENDOR', active=True, workspace_id=3).first()
    vendor.active = False
    vendor.save()

    response = api_client.get(url, {'attribute_type__in': 'VENDOR', 'limit': 10})
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response['results']) == 10


def test_qbo_field_view(mocker, api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/fields/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 1


def test_employee_view(mocker, api_client, test_connection):
    mocker.patch('apps.quickbooks_online.utils.QBOConnector.sync_employees', return_value=None)

    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/employees/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = response = api_client.get(url, {'attribute_type__in': 'EMPLOYEE', 'limit': 10})
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response['results']) == 2


def test_post_sync_dimensions(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/sync_dimensions/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)

    assert response.status_code == 200

    with mock.patch('apps.workspaces.models.Workspace.objects.get') as mock_call:
        mock_call.side_effect = Exception()

        response = api_client.post(url)
        assert response.status_code == 400

        mock_call.side_effect = QBOCredential.DoesNotExist()

        response = api_client.post(url)
        assert response.status_code == 400


def test_post_refresh_dimensions(api_client, test_connection):
    access_token = test_connection.access_token
    url = '/api/workspaces/3/qbo/refresh_dimensions/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)

    assert response.status_code == 200

    with mock.patch('apps.workspaces.models.Workspace.objects.get') as mock_call:
        mock_call.side_effect = Exception()

        response = api_client.post(url)
        assert response.status_code == 400

    qbo_credential = QBOCredential.get_active_qbo_credentials(3)
    qbo_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400
    response = json.loads(response.content)

    assert response['message'] == 'QBO credentials not found in workspace'


@pytest.mark.django_db(databases=['default'])
def test_qbo_webhook_complete_flow(api_client, test_connection):
    """
    Comprehensive test for QBO webhook flow covering:
    - URL routing and endpoint resolution
    - HMAC signature validation (valid/invalid)
    - HTTP 202 response for valid requests
    - Serializer logic and payload processing
    - Database persistence for single and multiple workspaces
    - End-to-end integration
    """
    qbo_credential_3 = QBOCredential.objects.get(workspace_id=3)
    original_realm_id_3 = qbo_credential_3.realm_id
    qbo_credential_3.realm_id = '123456789'
    qbo_credential_3.save()

    qbo_credential_4, created = QBOCredential.objects.get_or_create(
        workspace_id=4,
        defaults={
            'realm_id': '123456789',
            'refresh_token': 'test_token_4',
            'is_expired': False
        }
    )
    original_realm_id_4 = qbo_credential_4.realm_id
    if not created:
        qbo_credential_4.realm_id = '123456789'
        qbo_credential_4.save()

    webhook_token = 'test_webhook_secret_token'
    webhook_url = reverse('qbo-webhook-incoming')

    webhook_payload = data['webhook_payload_multi_entity']
    payload_json = json.dumps(webhook_payload)
    payload_bytes = payload_json.encode('utf-8')
    invalid_signature = 'invalid_signature_123'

    # Test 1: Invalid signature should return 403
    with override_settings(QBO_WEBHOOK_TOKEN=webhook_token):
        response = api_client.post(
            webhook_url,
            data=payload_json,
            content_type='application/json',
            **{'HTTP_INTUIT_SIGNATURE': invalid_signature}
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert QBOWebhookIncoming.objects.count() == 0

    # Test 2: Missing signature should return 403
    response = api_client.post(
        webhook_url,
        data=payload_json,
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert QBOWebhookIncoming.objects.count() == 0

    # Test 3: Valid signature should return 202 and create database records
    valid_signature = base64.b64encode(
        hmac.new(
            webhook_token.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).digest()
    ).decode('utf-8')

    with override_settings(QBO_WEBHOOK_TOKEN=webhook_token):
        response = api_client.post(
            webhook_url,
            data=payload_json,
            content_type='application/json',
            **{'HTTP_INTUIT_SIGNATURE': valid_signature}
        )

    assert response.status_code == status.HTTP_202_ACCEPTED

    # Verify database records were created for multi-workspace scenario
    webhooks = QBOWebhookIncoming.objects.all()
    assert webhooks.count() == 2

    # Verify first webhook record (Account entity)
    account_webhook = webhooks.filter(entity_type='Account').first()
    assert account_webhook is not None
    assert account_webhook.realm_id == '123456789'
    assert account_webhook.destination_id == '1'
    assert account_webhook.operation_type == 'Create'
    assert account_webhook.raw_response == webhook_payload

    # Verify workspace assignment (first credential should be primary)
    assert account_webhook.workspace_id == 3
    assert len(account_webhook.additional_workspace_ids) == 1
    assert 4 in account_webhook.additional_workspace_ids

    # Verify second webhook record (Item entity)
    item_webhook = webhooks.filter(entity_type='Item').first()
    assert item_webhook is not None
    assert item_webhook.destination_id == '2'
    assert item_webhook.operation_type == 'Update'
    assert item_webhook.workspace_id == 3
    assert 4 in item_webhook.additional_workspace_ids

    # Test 4: Single workspace scenario (different realm_id for only one workspace)
    qbo_credential_4.realm_id = '987654321'
    qbo_credential_4.save()

    single_workspace_payload = data['webhook_payload_single_entity']
    single_payload_json = json.dumps(single_workspace_payload)
    single_payload_bytes = single_payload_json.encode('utf-8')
    single_signature = base64.b64encode(
        hmac.new(
            webhook_token.encode('utf-8'),
            single_payload_bytes,
            hashlib.sha256
        ).digest()
    ).decode('utf-8')

    with override_settings(QBO_WEBHOOK_TOKEN=webhook_token):
        response = api_client.post(
            webhook_url,
            data=single_payload_json,
            content_type='application/json',
            **{'HTTP_INTUIT_SIGNATURE': single_signature}
        )

    assert response.status_code == status.HTTP_202_ACCEPTED

    # Verify single workspace webhook record
    vendor_webhook = QBOWebhookIncoming.objects.filter(entity_type='Vendor').first()
    assert vendor_webhook is not None
    assert vendor_webhook.realm_id == '987654321'
    assert vendor_webhook.workspace_id == 4
    assert vendor_webhook.additional_workspace_ids == []
    assert vendor_webhook.operation_type == 'Delete'

    # Verify total webhook count
    total_webhooks = QBOWebhookIncoming.objects.count()
    assert total_webhooks == 3

    # Test 5: URL pattern verification
    resolved = resolve(webhook_url)
    from apps.quickbooks_online.views import QBOWebhookIncomingView
    assert resolved.func.__name__ == QBOWebhookIncomingView.as_view().__name__

    # Test 6: Nonexistent realm_id should return 202 but create no records
    initial_count = QBOWebhookIncoming.objects.count()

    nonexistent_payload = data['webhook_payload_nonexistent_realm']
    nonexistent_payload_json = json.dumps(nonexistent_payload)
    nonexistent_bytes = nonexistent_payload_json.encode('utf-8')
    nonexistent_signature = base64.b64encode(
        hmac.new(
            webhook_token.encode('utf-8'),
            nonexistent_bytes,
            hashlib.sha256
        ).digest()
    ).decode('utf-8')

    with override_settings(QBO_WEBHOOK_TOKEN=webhook_token):
        response = api_client.post(
            webhook_url,
            data=nonexistent_payload_json,
            content_type='application/json',
            **{'HTTP_INTUIT_SIGNATURE': nonexistent_signature}
        )

    # Should still return 202 but no new records created
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert QBOWebhookIncoming.objects.count() == initial_count

    # Test 7: Exception handling should still return 202
    with override_settings(QBO_WEBHOOK_TOKEN=webhook_token):
        with patch('apps.quickbooks_online.serializers.QBOWebhookIncomingSerializer.create') as mock_create:
            mock_create.side_effect = Exception("Simulated processing error")

            exception_payload = data['webhook_payload_single_entity']
            exception_payload_json = json.dumps(exception_payload)
            exception_payload_bytes = exception_payload_json.encode('utf-8')
            exception_signature = base64.b64encode(
                hmac.new(
                    webhook_token.encode('utf-8'),
                    exception_payload_bytes,
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')

            response = api_client.post(
                webhook_url,
                data=exception_payload_json,
                content_type='application/json',
                **{'HTTP_INTUIT_SIGNATURE': exception_signature}
            )

            assert response.status_code == status.HTTP_202_ACCEPTED
            mock_create.assert_called_once()

    # Cleanup: Reset credentials to original state
    qbo_credential_3.realm_id = original_realm_id_3
    qbo_credential_3.save()
    qbo_credential_4.realm_id = original_realm_id_4
    qbo_credential_4.save()
