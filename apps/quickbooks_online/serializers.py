from rest_framework import serializers

from .models import Bill, BillLineitem


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
