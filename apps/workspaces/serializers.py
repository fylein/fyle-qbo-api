"""
Workspace Serializers
"""
from rest_framework import serializers

from .models import Workspace, WorkspaceSettings, WorkspaceSchedule, FyleCredential, QBOCredential


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Workspace serializer
    """
    class Meta:
        model = Workspace
        fields = '__all__'


class WorkspaceScheduleSerializer(serializers.ModelSerializer):
    """
    Workspace Schedule Serializer
    """
    class Meta:
        model = WorkspaceSchedule
        fields = '__all__'


class WorkspaceSettingsSerializer(serializers.ModelSerializer):
    """
    Workspace settings serializer
    """
    schedule = WorkspaceScheduleSerializer()

    class Meta:
        model = WorkspaceSettings
        fields = ['id', 'workspace', 'schedule', 'created_at', 'updated_at']


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
