"""
Workspace Serializers
"""
from rest_framework import serializers

from .models import Workspace, WorkspaceGeneralSettings, WorkspaceSchedule, FyleCredential,\
    QBOCredential, PastExportDetail


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


class WorkSpaceGeneralSettingsSerializer(serializers.ModelSerializer):
    """
    General settings serializer
    """
    class Meta:
        model = WorkspaceGeneralSettings
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


class PastExportDetailSerializer(serializers.ModelSerializer):
    """
    Past export detail serializer
    """
    class Meta:
        model = PastExportDetail
        fields = '__all__'
