import importlib
from typing import List, Dict

from django.db import models, transaction

from .exceptions import BulkError
from .utils import assert_valid

workspace_models = importlib.import_module("apps.workspaces.models")
Workspace = workspace_models.Workspace


def validate_mappings(source_type: str, destination_type: str, mappings: List[Dict], workspace_id: int):
	"""
	Validate Mappings Payload
	"""
	bulk_errors = []
	row = 0

	for mapping in mappings:
		if not source_type:
			bulk_errors.append({
				'row': row,
				'type': 'source type',
				'value': None,
				'message': 'source type not found'
			})

		if ('source_value' not in mapping) and (not mapping['source_value']):
			bulk_errors.append({
				'row': row,
				'type': 'source value',
				'value': None,
				'message': 'source value not found'
			})

		if not destination_type:
			bulk_errors.append({
				'row': row,
				'type': 'destination type',
				'value': None,
				'message': 'destination type not found'
			})

		if ('destination_value' not in mapping) and (not mapping['destination_value']):
			bulk_errors.append({
				'row': row,
				'type': 'destination value',
				'value': None,
				'message': 'destination value not found'
			})

		mapping_setting = MappingSetting.objects.filter(
			source_field=source_type,
			destination_field=destination_type
		).first()

		if not mapping_setting:
			bulk_errors.append({
				'row': row,
				'type': 'Setting',
				'value': '{0} / {1}'.format(source_type, destination_type),
				'message': 'Seeing not found'.format(
					source_type, mapping['source_value'])
			})

		expense_attribute = ExpenseAttribute.objects.filter(
			source_type=source_type,
			value=mapping['source_value'],
			workspace_id=workspace_id
		).first()

		if not expense_attribute:
			bulk_errors.append({
				'row': row,
				'type': source_type,
				'value': mapping['soure_value'],
				'message': 'Source type - {0}, Value - {1} not found'.format(
					source_type, mapping['source_value'])
			})

		destination_attribute = DestinationAttribute.objects.filter(
			destination_type=destination_type,
			value=mapping['destination_value'],
			workspace_id=workspace_id
		).first()

		if not destination_attribute:
			bulk_errors.append({
				'row': row,
				'type': destination_type,
				'value': mapping['destination_value'],
				'message': 'Destination type - {0}, Value - {1} not found'.format(
					destination_type, mapping['value'])
			})

		row = row + 1

	if bulk_errors:
		raise BulkError('Errors while creating mappings', bulk_errors)


def validate_mapping_settings(mappings_settings: List[Dict], workspace_id: int):
	expense_attribute_types = ExpenseAttribute.objects.filter(
			workspace_id=workspace_id).values('attribute_type').distinct()
	destination_attribute_types = DestinationAttribute.objects.filter(
			workspace_id=workspace_id).values('attribute_type').distinct()

	bulk_errors = []

	row = 0

	source_attributes = [setting['source_field'] for setting in mappings_settings]
	destination_attributes = [setting['destination_field'] for setting in mappings_settings]

	assert_valid(
		len(source_attributes) == len(list(set(source_attributes))),
		'source attributes cannot have duplicates'
	)

	assert_valid(
		len(destination_attributes) == len(list(set(destination_attributes))),
		'destination_attributes cannot have duplicates'
	)

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

		if mappings_setting['source_field'] not in expense_attribute_types:
			bulk_errors.append({
				'row': row,
				'value': mappings_setting['source_field'],
				'message': '{0} - Source field type not found'.format(mappings_setting['destination_field'])
			})

		if mappings_setting['destination_field'] not in destination_attribute_types:
			bulk_errors.append({
				'row': row,
				'value': mappings_setting['destination_field'],
				'message': '{0} - Destination field type not found'.format(mappings_setting['destination_field'])
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
				expense_attribute, _ = ExpenseAttribute.objects.get_or_create(
					attribute_type=attribute['attribute_type'],
					display_name=attribute['display_name'],
					value=attribute['value'],
					source_id=attribute['source_id'],
					workspace_id=workspace_id
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
				destination_attribute, _ = DestinationAttribute.objects.get_or_create(
					attribute_type=attribute['attribute_type'],
					display_name=attribute['display_name'],
					value=attribute['value'],
					destination_id=attribute['destination_id'],
					workspace_id=workspace_id
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

	class Meta:
		unique_together = (('source_field', 'workspace_id'), ('destination_field', 'workspace_id'))

	@staticmethod
	def bulk_upsert_mapping_setting(settings: List[Dict], workspace_id: int):
		"""
		Bulk update or create mapping setting
		"""
		validate_mapping_settings(settings, workspace_id)
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
	source = models.OneToOneField(ExpenseAttribute, on_delete=models.PROTECT)
	destination = models.ForeignKey(DestinationAttribute, on_delete=models.PROTECT)
	workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
	created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
	updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

	class Meta:
		unique_together = ('source_type', 'source', 'workspace')

	@staticmethod
	def bulk_upsert_mappings(source_type: str, destination_type: str, mappings: List[Dict], workspace_id: int):
		"""
		Bulk update or create mappings
		source_type = 'Type of Source attribute, eg. CATEGORY',
		destination_type = 'Type of Destination attribute, eg. ACCOUNT',
		mappings = [
			{
				'source_value': 'Source value to be mapped, eg. category name',
				'destination_value': 'Destination value to be mapped, eg. account name'
			}
		],
		workspace_id = Unique Workspace id
		"""
		validate_mappings(mappings, workspace_id)
		field_mappings = []

		with transaction.atomic():
			for mapping in mappings:
				mapping, _ = Mapping.objects.update_or_create(
					source_type=source_type,
					source=ExpenseAttribute.objects.get(
							source_type=source_type,
							value=mapping['source_value'],
							workspace_id=workspace_id
					),
					workspace=Workspace.objects.get(pk=workspace_id),
					defaults={
						'destination_type': destination_type,
						'destination': DestinationAttribute.objects.get(
							destination_type=destination_type,
							value=mapping['destination_value'],
							workspace_id=workspace_id
						)
					}
				)
				field_mappings.append(mapping)
			return field_mappings
