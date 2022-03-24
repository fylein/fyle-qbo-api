from rest_framework import serializers

from django.db import transaction

from fyle_accounting_mappings.models import MappingSetting

from apps.mappings.models import GeneralMapping

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings

class FilteredListSerializer(serializers.ListSerializer):
    """
    Serializer to filter the active system, which is a boolen field in
    System Model. The value argument to to_representation() method is
    the model instance
    """

    def to_representation(self, data):
        data = data.filter(destination_field__in=['CLASS', 'CUSTOMER', 'DEPARTMENT'])
        return super(FilteredListSerializer, self).to_representation(data)


class ReadWriteSerializerMethodField(serializers.SerializerMethodField):
    """
    Serializer Method Field to Read and Write from values
    Inherits serializers.SerializerMethodField
    """

    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['source'] = '*'
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        return {
            self.field_name: data
        }


class MappingSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MappingSetting
        list_serializer_class = FilteredListSerializer
        fields = ['source_field', 'destination_field', 'import_to_fyle', 'is_custom']


class WorkspaceGeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceGeneralSettings
        fields = ['import_categories', 'charts_of_accounts', 'import_tax_codes']


class GeneralMappingsSerializer(serializers.ModelSerializer):
    default_tax_code = ReadWriteSerializerMethodField()

    class Meta:
        model = GeneralMapping
        fields = [
            'default_tax_code'
        ]

    def get_default_tax_code(self, instance):
        return {
            'name': instance.default_tax_code_name,
            'id': instance.default_tax_code_id
        }


class ImportSettingsSerializer(serializers.Serializer):
    """
    Serializer for the ImportSettings Form/API
    """
    workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    general_mappings = GeneralMappingsSerializer()
    mapping_settings = MappingSettingSerializer(many=True)
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'workspace_general_settings',
            'general_mappings',
            'workspace_id'
        ]
        
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id
    
    def update(self, instance, validated):
        workspace_general_settings = validated.pop('workspace_general_settings')
        general_mappings = validated.pop('general_mappings')
        mapping_settings = validated.pop('mapping_settings')

        WorkspaceGeneralSettings.objects.update_or_create(
            workspace=instance,
            defaults={
                'import_categories': workspace_general_settings.get('import_categories'),
                'charts_of_accounts': workspace_general_settings.get('charts_of_accounts'),
                'import_tax_codes': workspace_general_settings.get('import_tax_codes')
            }
        )

        GeneralMapping.objects.update_or_create(
            workspace=instance,
            defaults={
                'default_tax_code_name': general_mappings.get('default_tax_code').get('name'),
                'default_tax_code_id': general_mappings.get('default_tax_code').get('id')
            }
        )
        with transaction.atomic():
            for setting in mapping_settings:
                mapping_setting, _ = MappingSetting.objects.update_or_create(
                    source_field=setting['source_field'],
                    workspace_id=instance.id,
                    defaults={
                        'destination_field': setting['destination_field'],
                        'import_to_fyle': setting['import_to_fyle'] if 'import_to_fyle' in setting else False,
                        'is_custom': setting['is_custom'] if 'is_custom' in setting else False
                    }
                )
                mapping_settings.append(mapping_setting)

        return instance

    def validate(self, data):
        if not data.get('workspace_general_settings'):
            raise serializers.ValidationError('Workspace general settings are required')

        if not data.get('expense_group_settings'):
            raise serializers.ValidationError('Expense group settings are required')

        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')
        return data