"""
Workspace Serializers
"""
from rest_framework import serializers

from .models import (
    FyleCredential,
    LastExportDetail,
    QBOCredential,
    Workspace,
    WorkspaceGeneralSettings,
    WorkspaceSchedule,
)


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Workspace serializer
    """

    class Meta:
        model = Workspace
        fields = "__all__"


class WorkspaceScheduleSerializer(serializers.ModelSerializer):
    """
    Workspace Schedule Serializer
    """

    class Meta:
        model = WorkspaceSchedule
        fields = "__all__"


class WorkSpaceGeneralSettingsSerializer(serializers.ModelSerializer):
    """
    General settings serializer
    """

    class Meta:
        model = WorkspaceGeneralSettings
        fields = "__all__"


class FyleCredentialSerializer(serializers.ModelSerializer):
    """
    Fyle credential serializer
    """

    class Meta:
        model = FyleCredential
        fields = "__all__"


class QBOCredentialSerializer(serializers.ModelSerializer):
    """
    QBO credential serializer
    """

    class Meta:
        model = QBOCredential
        fields = "__all__"


class LastExportDetailSerializer(serializers.ModelSerializer):
    """
    Last export detail serializer
    """

    class Meta:
        model = LastExportDetail
        fields = "__all__"
