from fyle_accounting_mappings.models import MappingSetting
from rest_framework import serializers

from apps.fyle.models import ExpenseGroupSettings
from apps.mappings.models import GeneralMapping
from apps.workspaces.apis.export_settings.triggers import ExportSettingsTrigger
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings


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
        fields = ['reimbursable_expenses_object', 'corporate_credit_card_expenses_object', 'name_in_journal_entry']


class ExpenseGroupSettingsSerializer(serializers.ModelSerializer):
    reimbursable_expense_group_fields = serializers.ListField(allow_null=True, required=False)
    reimbursable_export_date_type = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    corporate_credit_card_expense_group_fields = serializers.ListField(allow_null=True, required=False)
    ccc_export_date_type = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    ccc_expense_state = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    expense_state = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    split_expense_grouping = serializers.CharField(allow_null=False, allow_blank=False, required=True)

    class Meta:
        model = ExpenseGroupSettings
        fields = ['reimbursable_expense_group_fields', 'corporate_credit_card_expense_group_fields', 'expense_state', 'ccc_expense_state', 'reimbursable_export_date_type', 'ccc_export_date_type', 'split_expense_grouping']


class GeneralMappingsSerializer(serializers.ModelSerializer):
    accounts_payable = ReadWriteSerializerMethodField()
    qbo_expense_account = ReadWriteSerializerMethodField()
    bank_account = ReadWriteSerializerMethodField()
    default_ccc_account = ReadWriteSerializerMethodField()
    default_debit_card_account = ReadWriteSerializerMethodField()
    default_ccc_vendor = ReadWriteSerializerMethodField()

    class Meta:
        model = GeneralMapping
        fields = ['accounts_payable', 'qbo_expense_account', 'bank_account', 'default_ccc_account', 'default_debit_card_account', 'default_ccc_vendor']

    def get_accounts_payable(self, instance):
        return {'name': instance.accounts_payable_name, 'id': instance.accounts_payable_id}

    def get_qbo_expense_account(self, instance):
        return {'name': instance.qbo_expense_account_name, 'id': instance.qbo_expense_account_id}

    def get_bank_account(self, instance):
        return {'name': instance.bank_account_name, 'id': instance.bank_account_id}

    def get_default_ccc_account(self, instance):
        return {'name': instance.default_ccc_account_name, 'id': instance.default_ccc_account_id}

    def get_default_debit_card_account(self, instance):
        return {'name': instance.default_debit_card_account_name, 'id': instance.default_debit_card_account_id}

    def get_default_ccc_vendor(self, instance):
        return {'name': instance.default_ccc_vendor_name, 'id': instance.default_ccc_vendor_id}


class ExportSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the ExportSettings Form/API
    """

    workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    expense_group_settings = ExpenseGroupSettingsSerializer()
    general_mappings = GeneralMappingsSerializer()
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ['workspace_general_settings', 'expense_group_settings', 'general_mappings', 'workspace_id']
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id

    def update(self, instance, validated):
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        workspace_general_settings = validated.pop('workspace_general_settings')
        expense_group_settings = validated.pop('expense_group_settings')
        general_mappings = validated.pop('general_mappings')

        workspace_general_settings_instance = WorkspaceGeneralSettings.objects.filter(workspace_id=instance.id).first()
        old_configurations = {}
        if workspace_general_settings_instance:
            old_configurations = {
                'reimbursable_expenses_object': workspace_general_settings_instance.reimbursable_expenses_object,
                'corporate_credit_card_expenses_object': workspace_general_settings_instance.corporate_credit_card_expenses_object,
            }

        map_merchant_to_vendor = True
        category_sync_version = 'v2'
        if workspace_general_settings_instance:
            if workspace_general_settings_instance.map_merchant_to_vendor:
                map_merchant_to_vendor = workspace_general_settings_instance.map_merchant_to_vendor
            if workspace_general_settings_instance.category_sync_version:
                category_sync_version = workspace_general_settings_instance.category_sync_version

        enable_cards_mapping = True if workspace_general_settings.get('corporate_credit_card_expenses_object') and workspace_general_settings.get('corporate_credit_card_expenses_object') != 'BILL' else False

        WorkspaceGeneralSettings.objects.update_or_create(
            workspace=instance,
            defaults={
                'reimbursable_expenses_object': workspace_general_settings.get('reimbursable_expenses_object'),
                'corporate_credit_card_expenses_object': workspace_general_settings.get('corporate_credit_card_expenses_object'),
                'map_merchant_to_vendor': map_merchant_to_vendor,
                'category_sync_version': category_sync_version,
                'map_fyle_cards_qbo_account': enable_cards_mapping,
                'name_in_journal_entry': workspace_general_settings.get('name_in_journal_entry'),
            },
            user=user
        )

        export_trigger = ExportSettingsTrigger(workspace_general_settings, instance.id, old_configurations)

        export_trigger.post_save_workspace_general_settings()

        if enable_cards_mapping:
            MappingSetting.objects.update_or_create(destination_field='CREDIT_CARD_ACCOUNT', workspace_id=instance.id, defaults={'source_field': 'CORPORATE_CARD', 'import_to_fyle': False, 'is_custom': False}, user=user)

        if not expense_group_settings['reimbursable_expense_group_fields']:
            expense_group_settings['reimbursable_expense_group_fields'] = ['employee_email', 'report_id', 'fund_source']

        if not expense_group_settings['corporate_credit_card_expense_group_fields']:
            expense_group_settings['corporate_credit_card_expense_group_fields'] = ['employee_email', 'report_id', 'fund_source']

        if not expense_group_settings['reimbursable_export_date_type']:
            expense_group_settings['reimbursable_export_date_type'] = 'current_date'

        if not expense_group_settings['ccc_export_date_type']:
            expense_group_settings['ccc_export_date_type'] = 'current_date'

        expense_group_settings['import_card_credits'] = False

        if (
            workspace_general_settings.get('corporate_credit_card_expenses_object') in ('JOURNAL ENTRY', 'BILL', 'DEBIT CARD EXPENSE')
            or (map_merchant_to_vendor and workspace_general_settings['corporate_credit_card_expenses_object'] == 'CREDIT CARD PURCHASE')
            or (workspace_general_settings.get('reimbursable_expenses_object') in ('JOURNAL ENTRY', 'EXPENSE', 'BILL'))
        ):
            expense_group_settings['import_card_credits'] = True

        ExpenseGroupSettings.update_expense_group_settings(expense_group_settings, instance.id, user)

        GeneralMapping.objects.update_or_create(
            workspace=instance,
            defaults={
                'accounts_payable_name': general_mappings.get('accounts_payable').get('name'),
                'accounts_payable_id': general_mappings.get('accounts_payable').get('id'),
                'qbo_expense_account_name': general_mappings.get('qbo_expense_account').get('name'),
                'qbo_expense_account_id': general_mappings.get('qbo_expense_account').get('id'),
                'bank_account_name': general_mappings.get('bank_account').get('name'),
                'bank_account_id': general_mappings.get('bank_account').get('id'),
                'default_ccc_account_name': general_mappings.get('default_ccc_account').get('name'),
                'default_ccc_account_id': general_mappings.get('default_ccc_account').get('id'),
                'default_debit_card_account_name': general_mappings.get('default_debit_card_account').get('name'),
                'default_debit_card_account_id': general_mappings.get('default_debit_card_account').get('id'),
                'default_ccc_vendor_name': general_mappings.get('default_ccc_vendor').get('name'),
                'default_ccc_vendor_id': general_mappings.get('default_ccc_vendor').get('id'),
            },
            user=user
        )

        if instance.onboarding_state == 'EXPORT_SETTINGS':
            instance.onboarding_state = 'IMPORT_SETTINGS'
            instance.save()

        return instance

    def validate(self, data):
        if not data.get('workspace_general_settings'):
            raise serializers.ValidationError('Workspace general settings are required')

        if not data.get('expense_group_settings'):
            raise serializers.ValidationError('Expense group settings are required')

        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')
        return data
