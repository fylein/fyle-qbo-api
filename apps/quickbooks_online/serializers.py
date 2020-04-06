from rest_framework import serializers

from .models import Bill, BillLineitem, QuickbooksCheck, CheckLineitem


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
        model = QuickbooksCheck
        fields = '__all__'


class CheckLineitemsSerializer(serializers.ModelSerializer):
    """
    QBO Check Lineitems serializer
    """
    class Meta:
        model = CheckLineitem
        fields = '__all__'
