from rest_framework import serializers
from apps.workspaces.models import WorkspaceGeneralSettings, Workspace
from apps.fyle.models import ExpenseGroupSettings
from apps.mappings.models import GeneralMapping


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
        fields = ['reimbursable_expenses_object', 'corporate_credit_card_expenses_object']


class ExpenseGroupSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseGroupSettings
        fields = [
            'reimbursable_expense_group_fields',
            'corporate_credit_card_expense_group_fields',
            'expense_state',
            'reimbursable_export_date_type',
            'ccc_export_date_type'
        ]


class GeneralMappingsSerializer(serializers.ModelSerializer):
    accounts_payable = ReadWriteSerializerMethodField()
    qbo_expense_account = ReadWriteSerializerMethodField()
    bank_account = ReadWriteSerializerMethodField()
    default_ccc_account = ReadWriteSerializerMethodField()
    default_debit_card_account = ReadWriteSerializerMethodField()
    default_ccc_vendor = ReadWriteSerializerMethodField()

    class Meta:
        model = GeneralMapping
        fields = [
            'accounts_payable',
            'qbo_expense_account',
            'bank_account',
            'default_ccc_account',
            'default_debit_card_account',
            'default_ccc_vendor'
        ]

    def get_accounts_payable(self, instance):
        return {
            'name': instance.accounts_payable_name,
            'id': instance.accounts_payable_id
        }

    def get_qbo_expense_account(self, instance):
        return {
            'name': instance.qbo_expense_account_name,
            'id': instance.qbo_expense_account_id
        }

    def get_bank_account(self, instance):
        return {
            'name': instance.bank_account_name,
            'id': instance.bank_account_id
        }

    def get_default_ccc_account(self, instance):
        return {
            'name': instance.default_ccc_account_name,
            'id': instance.default_ccc_account_id
        }

    def get_default_debit_card_account(self, instance):
        return {
            'name': instance.default_debit_card_account_name,
            'id': instance.default_debit_card_account_id
        }

    def get_default_ccc_vendor(self, instance):
        return {
            'name': instance.default_ccc_vendor_name,
            'id': instance.default_ccc_vendor_id
        }


class ExportSettingsSerializer(serializers.Serializer):
    """
    Serializer for the ExportSettings Form/API
    """
    workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    expense_group_settings = ExpenseGroupSettingsSerializer()
    general_mappings = GeneralMappingsSerializer()
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'workspace_general_settings',
            'expense_group_settings',
            'general_mappings',
            'workspace_id'
        ]
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id

    def update(self, instance, validated):
        workspace_general_settings = validated.pop('workspace_general_settings')
        expense_group_settings = validated.pop('expense_group_settings')
        general_mappings = validated.pop('general_mappings')

        WorkspaceGeneralSettings.objects.update_or_create(
            workspace=instance,
            defaults={
                'reimbursable_expenses_object': workspace_general_settings.get('reimbursable_expenses_object'),
                'corporate_credit_card_expenses_object': workspace_general_settings.get(
                    'corporate_credit_card_expenses_object')
            }
        )

        ExpenseGroupSettings.objects.update_or_create(
            workspace=instance,
            defaults={
                'reimbursable_expense_group_fields': expense_group_settings.get('reimbursable_expense_group_fields'),
                'corporate_credit_card_expense_group_fields': expense_group_settings.get(
                    'corporate_credit_card_expense_group_fields'),
                'expense_state': expense_group_settings.get('expense_state'),
                'reimbursable_export_date_type': expense_group_settings.get('reimbursable_export_date_type'),
                'ccc_export_date_type': expense_group_settings.get('ccc_export_date_type')
            }
        )

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
                'default_ccc_vendor_id': general_mappings.get('default_ccc_vendor').get('id')
            }
        )
        return instance

    def validate(self, data):
        if not data.get('workspace_general_settings'):
            raise serializers.ValidationError('Workspace general settings are required')

        if not data.get('expense_group_settings'):
            raise serializers.ValidationError('Expense group settings are required')

        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')
        return data
