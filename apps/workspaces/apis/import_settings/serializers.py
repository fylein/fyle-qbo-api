from rest_framework import serializers

from apps.workspaces.models import Workspace



class ImportSettingsSerializer(serializers.Serializer):
    """
    Serializer for the ImportSettings Form/API
    """
    # workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    # general_mappings = GeneralMappingsSerializer()
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'workspace_general_settings',
            'expense_group_settings',
            'general_mappings',
            'workspace_id'
        ]
