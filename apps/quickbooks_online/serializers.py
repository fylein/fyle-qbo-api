from rest_framework import serializers

from fyle_accounting_mappings.models import DestinationAttribute
from .models import (
    Bill,
    BillLineitem,
    Cheque,
    ChequeLineitem,
    CreditCardPurchase,
    CreditCardPurchaseLineitem,
    JournalEntry,
    JournalEntryLineitem,
    QBOExpense,
    QBOExpenseLineitem,
)


class BillSerializer(serializers.ModelSerializer):
    """
    QBO Bill serializer
    """

    class Meta:
        model = Bill
        fields = "__all__"


class BillLineitemsSerializer(serializers.ModelSerializer):
    """
    QBO Bill Lineitems serializer
    """

    class Meta:
        model = BillLineitem
        fields = "__all__"


class ChequeSerializer(serializers.ModelSerializer):
    """
    QBO Cheque serializer
    """

    class Meta:
        model = Cheque
        fields = "__all__"


class ChequeLineitemsSerializer(serializers.ModelSerializer):
    """
    QBO Cheque Lineitems serializer
    """

    class Meta:
        model = ChequeLineitem
        fields = "__all__"


class CreditCardPurchaseSerializer(serializers.ModelSerializer):
    """
    QBO CreditCardPurchase serializer
    """

    class Meta:
        model = CreditCardPurchase
        fields = "__all__"


class CreditCardPurchaseLineitemsSerializer(serializers.ModelSerializer):
    """
    QBO CreditCardPurchaseS Lineitems serializer
    """

    class Meta:
        model = CreditCardPurchaseLineitem
        fields = "__all__"


class JournalEntrySerializer(serializers.ModelSerializer):
    """
    QBO JournalEntry serializer
    """

    class Meta:
        model = JournalEntry
        fields = "__all__"


class JournalEntryLineitemsSerializer(serializers.ModelSerializer):
    """
    QBO CreditCardPurchaseS Lineitems serializer
    """

    class Meta:
        model = JournalEntryLineitem
        fields = "__all__"


class QuickbooksFieldSerializer(serializers.ModelSerializer):
    """
    Expense Fields Serializer
    """

    class Meta:
        model = DestinationAttribute
        fields = ["attribute_type", "display_name"]
