from rest_framework import serializers

from apps.mappings.models import GeneralMapping
from apps.workspaces.apis.advanced_configurations.triggers import AdvancedConfigurationsTriggers
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings, WorkspaceSchedule
from apps.workspaces.tasks import schedule_sync


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


class WorkspaceGeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceGeneralSettings
        fields = ['sync_fyle_to_qbo_payments', 'sync_qbo_to_fyle_payments', 'auto_create_destination_entity', 'auto_create_merchants_as_vendors', 'je_single_credit_line', 'change_accounting_period', 'memo_structure']


class GeneralMappingsSerializer(serializers.ModelSerializer):
    bill_payment_account = ReadWriteSerializerMethodField()

    class Meta:
        model = GeneralMapping
        fields = ['bill_payment_account']

    def get_bill_payment_account(self, instance):
        return {'id': instance.bill_payment_account_id, 'name': instance.bill_payment_account_name}


class WorkspaceScheduleSerializer(serializers.ModelSerializer):
    emails_selected = serializers.ListField(allow_null=True, required=False)

    class Meta:
        model = WorkspaceSchedule
        fields = ['enabled', 'interval_hours', 'additional_email_options', 'emails_selected']


class AdvancedConfigurationsSerializer(serializers.ModelSerializer):
    """
    Serializer for the Advanced Configurations Form/API
    """

    workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    general_mappings = GeneralMappingsSerializer()
    workspace_schedules = WorkspaceScheduleSerializer()
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ['workspace_general_settings', 'general_mappings', 'workspace_schedules', 'workspace_id']
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id

    def update(self, instance, validated):
        workspace_general_settings = validated.pop('workspace_general_settings')
        general_mappings = validated.pop('general_mappings')
        workspace_schedules = validated.pop('workspace_schedules')

        workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
            workspace=instance,
            defaults={
                'sync_fyle_to_qbo_payments': workspace_general_settings.get('sync_fyle_to_qbo_payments'),
                'sync_qbo_to_fyle_payments': workspace_general_settings.get('sync_qbo_to_fyle_payments'),
                'auto_create_destination_entity': workspace_general_settings.get('auto_create_destination_entity'),
                'auto_create_merchants_as_vendors': workspace_general_settings.get('auto_create_merchants_as_vendors'),
                'je_single_credit_line': workspace_general_settings.get('je_single_credit_line'),
                'change_accounting_period': workspace_general_settings.get('change_accounting_period'),
                'memo_structure': workspace_general_settings.get('memo_structure'),
            },
        )

        GeneralMapping.objects.update_or_create(workspace=instance, defaults={'bill_payment_account_name': general_mappings.get('bill_payment_account').get('name'), 'bill_payment_account_id': general_mappings.get('bill_payment_account').get('id')})

        schedule_sync(
            workspace_id=instance.id,
            schedule_enabled=workspace_schedules.get('enabled'),
            hours=workspace_schedules.get('interval_hours'),
            email_added=workspace_schedules.get('additional_email_options'),
            emails_selected=workspace_schedules.get('emails_selected'),
        )

        AdvancedConfigurationsTriggers.run_workspace_general_settings_triggers(workspace_general_settings_instance)

        if instance.onboarding_state == 'ADVANCED_CONFIGURATION':
            instance.onboarding_state = 'COMPLETE'
            instance.save()
            AdvancedConfigurationsTriggers.post_to_integration_settings(instance.id, True)

        return instance

    def validate(self, data):
        if not data.get('workspace_general_settings'):
            raise serializers.ValidationError('Workspace general settings are required')

        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')

        if not data.get('workspace_schedules'):
            raise serializers.ValidationError('Workspace Schedules are required')

        return data
