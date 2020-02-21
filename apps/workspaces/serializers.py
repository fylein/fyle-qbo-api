"""
Workspace Serializers
"""
from django_q.models import Schedule
from rest_framework import serializers

from .models import Workspace, WorkspaceSettings, FyleCredential, QBOCredential


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Workspace serializer
    """
    class Meta:
        model = Workspace
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


class WorkspaceSettingsSerializer(serializers.ModelSerializer):
    """
    Workspace settings serializer
    """
    schedule = ScheduleSerializer()

    class Meta:
        model = WorkspaceSettings
        fields = ['id', 'workspace', 'schedule', 'schedule_enabled', 'created_at', 'updated_at']


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
