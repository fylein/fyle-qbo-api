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
    accounts = ReadWriteSerializerMethodField()
    customers = ReadWriteSerializerMethodField()
    classes = ReadWriteSerializerMethodField()
    department = ReadWriteSerializerMethodField()
    tax_codes = ReadWriteSerializerMethodField()

    class Meta:
        model = ImportSetting
        fields = [
            'accounts',
            'customers',
            'classes',
            'department',
            'tax_codes'
        ]

    def get_accounts(self, instance):
        return {
            'import_accounts': instance.import_accounts,
            'charts_of_accounts': instance.charts_of_accounts,
            'account_sync_version': instance.account_sync_version
        }
    
    def get_customers(self, instance):
        return {
            'import_customers': instance.import_customers,
            'customer_mapped_to': instance.customer_mapped_to
        }
    
    def get_classes(self, instance):
        return {
            'import_classes': instance.import_classes,
            'class_mapped_to': instance.class_mapped_to
        }
    
    def get_department(self, instance):
        return {
            'import_departments': instance.import_departments,
            'department_mapped_to': instance.department_mapped_to
        }
    
    def get_tax_codes(self, instance):
        return {
            'import_tax_codes': instance.import_tax_codes
        }


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
                'import_accounts': import_settings.get('accounts').get('import_accounts'),
                'charts_of_accounts': import_settings.get('accounts').get('charts_of_accounts'),
                'account_sync_version': import_settings.get('accounts').get('account_sync_version'),
                'import_customers': import_settings.get('customers').get('import_customers'),
                'customer_mapped_to': import_settings.get('customers').get('customer_mapped_to'),
                'import_classes': import_settings.get('classes').get('import_classes'),
                'class_mapped_to': import_settings.get('classes').get('class_mapped_to'),
                'import_departments': import_settings.get('department').get('import_departments'),
                'department_mapped_to': import_settings.get('department').get('department_mapped_to'),
                'import_tax_codes': import_settings.get('tax_codes').get('import_tax_codes')
            }
        )

        return instance

    def validate(self, data):
        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')

        if not data.get('import_settings'):
            raise serializers.ValidationError('Import Settings are required')
        return data
