from django.db import transaction
from fyle_accounting_mappings.models import MappingSetting
from rest_framework import serializers

from apps.mappings.models import GeneralMapping
from apps.workspaces.apis.import_settings.triggers import ImportSettingsTrigger
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from fyle_integrations_imports.models import ImportLog


class MappingSettingFilteredListSerializer(serializers.ListSerializer):
    """
    Serializer to filter the active system, which is a boolen field in
    System Model. The value argument to to_representation() method is
    the model instance
    """

    def to_representation(self, data):
        data = data.filter(destination_field__in=['CLASS', 'CUSTOMER', 'DEPARTMENT'])
        return super(MappingSettingFilteredListSerializer, self).to_representation(data)


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


class MappingSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MappingSetting
        list_serializer_class = MappingSettingFilteredListSerializer
        fields = ['source_field', 'destination_field', 'import_to_fyle', 'is_custom', 'source_placeholder']


class WorkspaceGeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceGeneralSettings
        fields = ['import_categories', 'import_items', 'charts_of_accounts', 'import_tax_codes', 'import_vendors_as_merchants', 'import_code_fields']


class GeneralMappingsSerializer(serializers.ModelSerializer):
    default_tax_code = ReadWriteSerializerMethodField()

    class Meta:
        model = GeneralMapping
        fields = ['default_tax_code']

    def get_default_tax_code(self, instance):
        return {'name': instance.default_tax_code_name, 'id': instance.default_tax_code_id}


class ImportSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the ImportSettings Form/API
    """

    workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    general_mappings = GeneralMappingsSerializer()
    mapping_settings = MappingSettingSerializer(many=True)
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ['workspace_general_settings', 'general_mappings', 'mapping_settings', 'workspace_id']
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id

    def update(self, instance, validated):
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        workspace_general_settings = validated.pop('workspace_general_settings')
        general_mappings = validated.pop('general_mappings')
        mapping_settings = validated.pop('mapping_settings')

        # Check if there is a diff in charts of accounts
        # Update the last_successful_run_at to None for Category Import Log
        if workspace_general_settings.get('charts_of_accounts') != instance.workspace_general_settings.charts_of_accounts \
            or (workspace_general_settings.get('import_items') and not instance.workspace_general_settings.import_items):
            category_import_log = ImportLog.objects.filter(workspace_id=instance.id, attribute_type='CATEGORY').first()

            if category_import_log:
                category_import_log.last_successful_run_at = None
                category_import_log.save()

        pre_save_workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=instance.id).first()

        workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
            workspace=instance,
            defaults={
                'import_categories': workspace_general_settings.get('import_categories'),
                'import_items': workspace_general_settings.get('import_items'),
                'charts_of_accounts': workspace_general_settings.get('charts_of_accounts'),
                'import_tax_codes': workspace_general_settings.get('import_tax_codes'),
                'import_vendors_as_merchants': workspace_general_settings.get('import_vendors_as_merchants'),
                'import_code_fields': workspace_general_settings.get('import_code_fields'),
            },
            user=user
        )

        GeneralMapping.objects.update_or_create(workspace=instance, defaults={'default_tax_code_name': general_mappings.get('default_tax_code').get('name'), 'default_tax_code_id': general_mappings.get('default_tax_code').get('id')}, user=user)

        trigger: ImportSettingsTrigger = ImportSettingsTrigger(workspace_general_settings=workspace_general_settings, mapping_settings=mapping_settings, workspace_id=instance.id)

        trigger.post_save_workspace_general_settings(workspace_general_settings_instance, pre_save_workspace_general_settings)
        trigger.pre_save_mapping_settings(pre_save_workspace_general_settings)

        if workspace_general_settings['import_tax_codes']:
            mapping_settings.append({'source_field': 'TAX_GROUP', 'destination_field': 'TAX_CODE', 'import_to_fyle': True, 'is_custom': False})

        mapping_settings.append({'source_field': 'CATEGORY', 'destination_field': 'ACCOUNT', 'import_to_fyle': False, 'is_custom': False})

        with transaction.atomic():
            for setting in mapping_settings:
                MappingSetting.objects.update_or_create(
                    destination_field=setting['destination_field'],
                    workspace_id=instance.id,
                    defaults={
                        'source_field': setting['source_field'],
                        'import_to_fyle': setting['import_to_fyle'] if 'import_to_fyle' in setting else False,
                        'is_custom': setting['is_custom'] if 'is_custom' in setting else False,
                        'source_placeholder': setting['source_placeholder'] if 'source_placeholder' in setting else None,
                    },
                    user=user
                )

        trigger.post_save_mapping_settings(workspace_general_settings_instance)

        if instance.onboarding_state == 'IMPORT_SETTINGS':
            instance.onboarding_state = 'ADVANCED_CONFIGURATION'
            instance.save()

        return instance

    def validate(self, data):
        if not data.get('workspace_general_settings'):
            raise serializers.ValidationError('Workspace general settings are required')

        if data.get('mapping_settings') is None:
            raise serializers.ValidationError('Mapping settings are required')

        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')

        workspace_id = getattr(self.instance, 'id', None)
        if not workspace_id:
            workspace_id = self.context['request'].parser_context.get('kwargs').get('workspace_id')
        general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
        import_logs = ImportLog.objects.filter(workspace_id=workspace_id).values_list('attribute_type', flat=True)

        is_errored = False
        old_code_pref_list = set()

        if general_settings:
            old_code_pref_list = set(general_settings.import_code_fields)

        new_code_pref_list = set(data.get('workspace_general_settings', {}).get('import_code_fields', []))
        diff_code_pref_list = list(old_code_pref_list.symmetric_difference(new_code_pref_list))

        if 'ACCOUNT' in diff_code_pref_list and 'CATEGORY' in import_logs:
            is_errored = True

        if not old_code_pref_list.issubset(new_code_pref_list):
            is_errored = True

        if is_errored:
            raise serializers.ValidationError('Cannot change the code fields once they are imported')

        return data
