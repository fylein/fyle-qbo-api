from rest_framework import serializers

from apps.workspaces.models import WorkspaceGeneralSettings

from .triggers import MapEmployeesTriggers

class WorkspaceGeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceGeneralSettings
        fields = ['employee_field_mapping', 'auto_map_employees']


class MapEmployeesSerializer(serializers.ModelSerializer):
    workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceGeneralSettings
        fields = [
            'workspace_general_settings',
            'workspace_id'
        ]

    def get_workspace_id(self, instance):
        return instance.id

    def update(self, instance, validated_data):
        workspace_id = instance.id
        workspace_general_settings = validated_data.pop('workspace_general_settings')

        workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
            workspace_id=workspace_id,
            defaults={
                'employee_field_mapping': workspace_general_settings['employee_field_mapping'],
                'auto_map_employees': workspace_general_settings['auto_map_employees']
            }
        )

        MapEmployeesTriggers.run_workspace_general_settings_triggers(workspace_general_settings_instance)

        return instance

    def validate(self, data):
        if not data.get('workspace_general_settings').get('employee_field_mapping'):
            raise serializers.ValidationError('employee_field_mapping field is required')

        if not data.get('workspace_general_settings').get('auto_map_employees'):
            raise serializers.ValidationError('auto_map_employees field is required')

        if data.get('workspace_general_settings').get('auto_map_employees') and \
            data.get('workspace_general_settings').get('auto_map_employees') not in ['EMAIL', 'NAME', 'EMPLOYEE_CODE']:
            raise serializers.ValidationError('auto_map_employees can have only EMAIL / NAME / EMPLOYEE_CODE')

        return data
