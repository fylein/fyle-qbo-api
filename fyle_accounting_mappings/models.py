import importlib
from typing import List, Dict

from django.db import models, transaction

from .exceptions import BulkError
from .utils import assert_valid

workspace_models = importlib.import_module("apps.workspaces.models")
Workspace = workspace_models.Workspace


def validate_mapping_settings(mappings_settings: List[Dict]):
    bulk_errors = []

    row = 0

    for mappings_setting in mappings_settings:
        if ('source_field' not in mappings_setting) and (not mappings_setting['source_field']):
            bulk_errors.append({
                'row': row,
                'value': None,
                'message': 'source field cannot be empty'
            })

        if ('destination_field' not in mappings_setting) and (not mappings_setting['destination_field']):
            bulk_errors.append({
                'row': row,
                'value': None,
                'message': 'destination field cannot be empty'
            })

        row = row + 1

    if bulk_errors:
        raise BulkError('Errors while creating settings', bulk_errors)


class ExpenseAttribute(models.Model):
    """
    Fyle Expense Attributes
    """
    id = models.AutoField(primary_key=True)
    attribute_type = models.CharField(max_length=255, help_text='Type of expense attribute')
    display_name = models.CharField(max_length=255, help_text='Display name of expense attribute')
    value = models.CharField(max_length=255, help_text='Value of expense attribute')
    source_id = models.CharField(max_length=255, help_text='Fyle ID')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    @staticmethod
    def bulk_upsert_expense_attributes(attributes: List[Dict], workspace_id):
        """
        Get or create expense attributes
        """
        expense_attributes = []

        with transaction.atomic():
            for attribute in attributes:
                expense_attribute, _ = ExpenseAttribute.objects.update_or_create(
                    attribute_type=attribute['attribute_type'],
                    value=attribute['value'],
                    workspace_id=workspace_id,
                    defaults={
                        'source_id': attribute['source_id'],
                        'display_name': attribute['display_name'],
                    }
                )
                expense_attributes.append(expense_attribute)
            return expense_attributes


class DestinationAttribute(models.Model):
    """
    Destination Expense Attributes
    """
    id = models.AutoField(primary_key=True)
    attribute_type = models.CharField(max_length=255, help_text='Type of expense attribute')
    display_name = models.CharField(max_length=255, help_text='Display name of attribute')
    value = models.CharField(max_length=255, help_text='Value of expense attribute')
    destination_id = models.CharField(max_length=255, help_text='Destination ID')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    @staticmethod
    def bulk_upsert_destination_attributes(attributes: List[Dict], workspace_id):
        """
        get or create destination attributes
        """
        destination_attributes = []
        with transaction.atomic():
            for attribute in attributes:
                destination_attribute, _ = DestinationAttribute.objects.update_or_create(
                    attribute_type=attribute['attribute_type'],
                    value=attribute['value'],
                    workspace_id=workspace_id,
                    defaults={
                        'display_name': attribute['display_name'],
                        'destination_id': attribute['destination_id']
                    }
                )
                destination_attributes.append(destination_attribute)
            return destination_attributes


class MappingSetting(models.Model):
    """
    Mapping Settings
    """
    id = models.AutoField(primary_key=True)
    source_field = models.CharField(max_length=255, help_text='Source mapping field')
    destination_field = models.CharField(max_length=40, help_text='Destination mapping field', null=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    @staticmethod
    def bulk_upsert_mapping_setting(settings: List[Dict], workspace_id: int):
        """
        Bulk update or create mapping setting
        """
        validate_mapping_settings(settings)
        mapping_settings = []

        with transaction.atomic():
            for setting in settings:
                mapping_setting, _ = MappingSetting.objects.get_or_create(
                    source_field=setting['source_field'],
                    workspace_id=workspace_id,
                    destination_field=setting['destination_field']
                )
                mapping_settings.append(mapping_setting)

            return mapping_settings


class Mapping(models.Model):
    """
    Mappings
    """
    id = models.AutoField(primary_key=True)
    source_type = models.CharField(max_length=255, help_text='Fyle Enum')
    destination_type = models.CharField(max_length=255, help_text='Destination Enum')
    source = models.ForeignKey(ExpenseAttribute, on_delete=models.PROTECT)
    destination = models.ForeignKey(DestinationAttribute, on_delete=models.PROTECT)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        unique_together = ('source_type', 'source', 'destination_type', 'workspace')

    @staticmethod
    def create_or_update_mapping(source_type: str, destination_type: str,
                                 source_value: str, destination_value: str, workspace_id: int):
        """
        Bulk update or create mappings
        source_type = 'Type of Source attribute, eg. CATEGORY',
        destination_type = 'Type of Destination attribute, eg. ACCOUNT',
        source_value = 'Source value to be mapped, eg. category name',
        destination_value = 'Destination value to be mapped, eg. account name'
        workspace_id = Unique Workspace id
        """
        settings = MappingSetting.objects.filter(source_field=source_type, destination_field=destination_type,
                                                 workspace_id=workspace_id).first()

        assert_valid(
            settings is not None and settings != [],
            'Settings for Destination  {0} / Source {1} not found'.format(destination_type, source_type)
        )

        mapping, _ = Mapping.objects.update_or_create(
            source_type=source_type,
            source=ExpenseAttribute.objects.get(
                attribute_type=source_type, value=source_value, workspace_id=workspace_id
            ) if source_value else None,
            destination_type=destination_type,
            workspace=Workspace.objects.get(pk=workspace_id),
            defaults={
                'destination': DestinationAttribute.objects.get(
                    attribute_type=destination_type,
                    value=destination_value,
                    workspace_id=workspace_id
                )
            }
        )
        return mapping
