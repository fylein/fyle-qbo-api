"""
Mapping Serializers
"""
from rest_framework import serializers
from .models import ExpenseAttribute, DestinationAttribute, MappingSetting, Mapping


class ExpenseAttributeSerializer(serializers.ModelSerializer):
    """
    Expense Attribute serializer
    """
    class Meta:
        model = ExpenseAttribute
        fields = '__all__'


class DestinationAttributeSerializer(serializers.ModelSerializer):
    """
    Destination Attribute serializer
    """
    class Meta:
        model = DestinationAttribute
        fields = '__all__'


class MappingSettingSerializer(serializers.ModelSerializer):
    """
    Mapping Setting serializer
    """
    class Meta:
        model = MappingSetting
        fields = '__all__'


class MappingSerializer(serializers.ModelSerializer):
    """
    Mapping serializer
    """
    source = ExpenseAttributeSerializer()
    destination = DestinationAttributeSerializer()

    class Meta:
        model = Mapping
        fields = '__all__'
