import logging

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
    QBOWebhookIncoming,
)
from apps.workspaces.models import QBOCredential

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


class QBOWebhookIncomingSerializer(serializers.Serializer):
    """
    Serializer for QBO webhook data collection
    """

    def create(self):
        """
        Process and store webhook data for all workspaces
        """
        request = self.context['request']
        payload = request.data
        webhook_objects = []

        for event_notification in payload.get('eventNotifications', []):
            realm_id = event_notification.get('realmId')
            qbo_credentials = QBOCredential.objects.filter(realm_id=realm_id).order_by('created_at')
            if not qbo_credentials.exists():
                logger.warning(f"No workspace found for realm_id: {realm_id}")
                continue

            primary_workspace = qbo_credentials.first().workspace
            additional_workspace_ids = list(qbo_credentials.values_list('workspace_id', flat=True)[1:])

            data_change_event = event_notification.get('dataChangeEvent', {})
            entities = data_change_event.get('entities', [])

            for entity in entities:
                webhook_objects.append(
                    QBOWebhookIncoming(
                        workspace=primary_workspace,
                        additional_workspace_ids=additional_workspace_ids,
                        realm_id=realm_id,
                        entity_type=entity.get('name'),
                        destination_id=entity.get('id'),
                        operation_type=entity.get('operation'),
                        last_updated_at=entity.get('lastUpdated'),
                        raw_response=payload
                    )
                )

        if webhook_objects:
            QBOWebhookIncoming.objects.bulk_create(webhook_objects)

        return {}
