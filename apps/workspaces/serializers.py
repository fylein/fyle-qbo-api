"""
Workspace Serializers
"""
from rest_framework import serializers

from .models import Workspace, FyleCredential, QBOCredential


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Workspace serializer
    """
    class Meta:
        model = Workspace
        fields = '__all__'


class FyleCredentialSerializer(serializers.ModelSerializer):
    """
    Fyle credential serializer
    """
    class Meta:
        model = FyleCredential
        fields = '__all__'


class QBOCredentialSerializer(serializers.ModelSerializer):
    """
    QBO credential serializer
    """
    class Meta:
        model = QBOCredential
        fields = '__all__'
