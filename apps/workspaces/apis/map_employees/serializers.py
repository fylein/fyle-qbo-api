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
    onboarding_state = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceGeneralSettings
        fields = [
            'workspace_general_settings',
            'workspace_id',
            'onboarding_state'
        ]

    def get_workspace_id(self, instance):
        return instance.id

    def get_onboarding_state(self, instance):
        return instance.onboarding_state

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

        if instance.onboarding_state != 'COMPLETE':
            instance.onboarding_state = 'MAP_EMPLOYEES'
            instance.save()

        return instance

    def validate(self, data):
        if not data.get('workspace_general_settings').get('employee_field_mapping'):
            raise serializers.ValidationError('employee_field_mapping field is required')

        if not data.get('workspace_general_settings').get('auto_map_employees'):
            raise serializers.ValidationError('auto_map_employees field is required')

        if 'auto_map_employees' in data.get('workspace_general_settings') and \
            data.get('workspace_general_settings').get('auto_map_employees') not in ['EMAIL', 'NAME', 'EMPLOYEE_CODE']:
            raise serializers.ValidationError('auto_map_employees can have only EMAIL / NAME / EMPLOYEE_CODE')

        return data
