from rest_framework import serializers

from .models import Bill, BillLineitem, Cheque, CheckLineitem, CreditCardPurchase, CreditCardPurchaseLineitem,\
    JournalEntry, JournalEntryLineitem


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


class CheckSerializer(serializers.ModelSerializer):
    """
    QBO Check serializer
    """
    class Meta:
        model = Cheque
        fields = '__all__'


class CheckLineitemsSerializer(serializers.ModelSerializer):
    """
    QBO Check Lineitems serializer
    """
    class Meta:
        model = CheckLineitem
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
