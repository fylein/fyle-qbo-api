from rest_framework import serializers

from apps.mappings.tasks import schedule_auto_map_employees
from apps.workspaces.models import WorkspaceGeneralSettings


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

        created_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
            workspace_id=workspace_id,
            defaults={
                'employee_field_mapping': validated_data['employee_field_mapping'],
                'auto_map_employees': validated_data['auto_map_employees']
            }
        )

        schedule_auto_map_employees(validated_data['auto_map_employees'], workspace_id)

        return created_instance
