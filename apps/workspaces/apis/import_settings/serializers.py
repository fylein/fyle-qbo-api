from rest_framework import serializers
from apps.workspaces.models import Workspace
from apps.mappings.models import GeneralMapping

from .models import ImportSetting


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
        return {self.field_name: data}


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


class ImportSettingsModelSerializer(serializers.Serializer):
    class Meta:
        model = ImportSetting
        fields = [
            'import_accounts',
            'chart_of_accounts',
            'account_sync_version',
            'import_customers',
            'customers_mapped_to',
            'import_classes',
            'classes_mapped_to',
            'import_departments',
            'departments_mapped_to',
            'import_tax_codes'
        ]


class ImportSettingsSerializer(serializers.Serializer):
    """
    Serializer for the ExportSettings Form/API
    """
    general_mappings = GeneralMappingsSerializer()
    import_settings = ImportSettingsModelSerializer()
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'general_mappings', 
            'import_settings', 
            'workspace_id'
        ]
        read_only_fields = ['workspace_id']
    
    def get_workspace_id(self, instance):
        return instance.id
    
    def update(self, instance, validated):
        import_settings = validated.pop('import_settings')
        general_mappings = validated.pop('general_mappings')


        GeneralMapping.objects.update_or_create(
            workspace=instance,
            defaults={
                'default_tax_code_id': general_mappings.get('default_tax_code').get('id'),
                'default_tax_code_name': general_mappings.get('default_tax_code').get('name')
            }
        )

        ImportSetting.objects.update_or_create(
            workspace=instance,
            defaults={
                'import_accounts': import_settings.get('import_accounts'),
                'chart_of_accounts': import_settings.get('chart_of_accounts'),
                'account_sync_version': import_settings.get('account_sync_version'),
                'import_customers': import_settings.get('import_customers'),
                'customers_mapped_to': import_settings.get('customers_mapped_to'),
                'import_classes': import_settings.get('import_classes'),
                'classes_mapped_to': import_settings.get('classes_mapped_to'),
                'import_departments': import_settings.get('import_departments'),
                'departments_mapped_to': import_settings.get('departments_mapped_to'),
                'import_tax_codes': import_settings.get('import_tax_codes')
            }
        )

        return instance

    def validate(self, data):
        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')

        if not data.get('import_settings'):
            raise serializers.ValidationError('Import Settings are required')
        return data
