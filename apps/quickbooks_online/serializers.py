import logging
import os

from fyle_accounting_mappings.models import DestinationAttribute
from rest_framework import serializers

from apps.quickbooks_online.models import (
    Bill,
    BillLineitem,
    Cheque,
    ChequeLineitem,
    CreditCardPurchase,
    CreditCardPurchaseLineitem,
    JournalEntry,
    JournalEntryLineitem,
    WebhookData,
)
from apps.workspaces.models import QBOCredential
from fyle_qbo_api.utils import validate_webhook_signature

logger = logging.getLogger(__name__)


class BillSerializer(serializers.ModelSerializer):
    """
    QBO Bill serializer
    """

    class Meta:
        model = Bill
        fields = '__all__'


class BillLineitemsSerializer(serializers.ModelSerializer):
    """
    QBO Bill Lineitems serializer
    """

    class Meta:
        model = BillLineitem
        fields = '__all__'


class ChequeSerializer(serializers.ModelSerializer):
    """
    QBO Cheque serializer
    """

    class Meta:
        model = Cheque
        fields = '__all__'


class ChequeLineitemsSerializer(serializers.ModelSerializer):
    """
    QBO Cheque Lineitems serializer
    """

    class Meta:
        model = ChequeLineitem
        fields = '__all__'


class CreditCardPurchaseSerializer(serializers.ModelSerializer):
    """
    QBO CreditCardPurchase serializer
    """

    class Meta:
        model = CreditCardPurchase
        fields = '__all__'


class CreditCardPurchaseLineitemsSerializer(serializers.ModelSerializer):
    """
    QBO CreditCardPurchaseS Lineitems serializer
    """

    class Meta:
        model = CreditCardPurchaseLineitem
        fields = '__all__'


class JournalEntrySerializer(serializers.ModelSerializer):
    """
    QBO JournalEntry serializer
    """

    class Meta:
        model = JournalEntry
        fields = '__all__'


class JournalEntryLineitemsSerializer(serializers.ModelSerializer):
    """
    QBO CreditCardPurchaseS Lineitems serializer
    """

    class Meta:
        model = JournalEntryLineitem
        fields = '__all__'


class QuickbooksFieldSerializer(serializers.ModelSerializer):
    """
    Expense Fields Serializer
    """

    class Meta:
        model = DestinationAttribute
        fields = ['attribute_type', 'display_name']


class QBOWebhookSerializer(serializers.Serializer):
    """
    Serializer for QBO webhook data collection
    """

    def create(self, validated_data):
        """
        Process and store webhook data
        """
        request = self.context['request']

        raw_body = request.body
        signature = request.headers.get('intuit-signature')
        payload = request.data

        if not validate_webhook_signature(raw_body, signature, os.getenv('QBO_WEBHOOK_TOKEN')):
            logger.error('Invalid signature')
            return

        for event_notification in payload.get('eventNotifications', []):
            realm_id = event_notification.get('realmId')

            try:
                qbo_credential = QBOCredential.objects.select_related('workspace').filter(realm_id=realm_id).order_by('-created_at').first()
                workspace = qbo_credential.workspace

                data_change_event = event_notification.get('dataChangeEvent', {})
                entities = data_change_event.get('entities', [])

                for entity in entities:
                    WebhookData.objects.create(
                        workspace=workspace,
                        realm_id=realm_id,
                        entity_type=entity.get('name'),
                        entity_id=entity.get('id'),
                        operation=entity.get('operation'),
                        last_updated=entity.get('lastUpdated'),
                        raw_payload=payload
                    )
            except QBOCredential.DoesNotExist:
                logger.warning(f"No workspace found for realm_id: {realm_id}")
                continue
