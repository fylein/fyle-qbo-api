from rest_framework import serializers

from apps.workspaces.models import WorkspaceGeneralSettings

from .triggers import MapEmployeesTriggers


class MapEmployeesSerializer(serializers.ModelSerializer):
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceGeneralSettings
        fields = [
            'employee_field_mapping',
            'auto_map_employees',
            'workspace_id'
        ]

    def get_workspace_id(self, instance):
        return instance.workspace_id

    def create(self, validated_data):
        workspace_id = self.context['view'].kwargs['workspace_id']

        workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
            workspace_id=workspace_id,
            defaults={
                'employee_field_mapping': validated_data['employee_field_mapping'],
                'auto_map_employees': validated_data['auto_map_employees']
            }
        )

        MapEmployeesTriggers.run_workspace_general_settings_triggers(workspace_general_settings_instance)

        return workspace_general_settings_instance

    def validate(self, data):
        if not data.get('employee_field_mapping'):
            raise serializers.ValidationError('employee_field_mapping field is required')

        if not data.get('auto_map_employees'):
            raise serializers.ValidationError('auto_map_employees field is required')

        if 'auto_map_employees' in data and data.get('auto_map_employees') not in ['EMAIL', 'NAME', 'EMPLOYEE_CODE']:
            raise serializers.ValidationError('auto_map_employees can have only EMAIL / NAME / EMPLOYEE_CODE')

        return data
