from rest_framework import serializers

from apps.mappings.models import GeneralMapping


class GeneralMappingSerializer(serializers.ModelSerializer):
    """
    General mappings group serializer
    """

    class Meta:
        model = GeneralMapping
        fields = '__all__'
