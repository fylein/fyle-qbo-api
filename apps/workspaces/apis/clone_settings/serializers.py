from apps.workspaces.models import Workspace
from rest_framework import serializers

from django.db import transaction

from apps.workspaces.apis.export_settings.serializers import (
    ExportSettingsSerializer, ReadWriteSerializerMethodField
)

from apps.workspaces.apis.import_settings.serializers import ImportSettingsSerializer
from apps.workspaces.apis.advanced_configurations.serializers import AdvancedConfigurationsSerializer
from apps.workspaces.apis.map_employees.serializers import MapEmployeesSerializer


class CloneSettingsSerializer(serializers.ModelSerializer):
    export_settings = ReadWriteSerializerMethodField()
    import_settings = ReadWriteSerializerMethodField()
    advanced_configurations = ReadWriteSerializerMethodField()
    employee_mappings = ReadWriteSerializerMethodField()
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'workspace_id',
            'export_settings',
            'import_settings',
            'advanced_configurations',
            'employee_mappings'
        ]
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id

    def get_export_settings(self, instance):
        return ExportSettingsSerializer(instance).data

    def get_import_settings(self, instance):
        return ImportSettingsSerializer(instance).data

    def get_advanced_configurations(self, instance):
        return AdvancedConfigurationsSerializer(instance).data

    def get_employee_mappings(self, instance):
        return MapEmployeesSerializer(instance).data

    def update(self, instance, validated):
        export_settings = validated.pop('export_settings')
        import_settings = validated.pop('import_settings')
        advanced_configurations = validated.pop('advanced_configurations')
        employee_mapping = validated.pop('employee_mappings')

        export_settings_serializer = ExportSettingsSerializer(
            instance, data=export_settings, partial=True
        )

        import_settings_serializer = ImportSettingsSerializer(
            instance, data=import_settings, partial=True
        )

        advanced_configurations_serializer = AdvancedConfigurationsSerializer(
            instance, data=advanced_configurations, partial=True
        )

        employee_mapping_serializer = MapEmployeesSerializer(
            instance, data=employee_mapping, partial=True
        )

        if export_settings_serializer.is_valid(raise_exception=True) and employee_mapping_serializer.is_valid(raise_exception=True) \
            and import_settings_serializer.is_valid(raise_exception=True) and  \
            advanced_configurations_serializer.is_valid(raise_exception=True):

            with transaction.atomic():
                export_settings_serializer.save()
                import_settings_serializer.save()
                advanced_configurations_serializer.save()
                employee_mapping_serializer.save()

        return instance

    def validate(self, data):
        if not data.get('export_settings'):
            raise serializers.ValidationError('Export Settings are required')

        if not data.get('import_settings'):
            raise serializers.ValidationError('Import Settings are required')

        if not data.get('advanced_configurations'):
            raise serializers.ValidationError('Advanced Settings are required')

        if not data.get('employee_mappings'):
            raise serializers.ValidationError('Employee Mappings are required')
        return data
