"""
Mapping Signals
"""
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.mappings.tasks import upload_attributes_to_fyle
from apps.tasks.models import Error
from apps.workspaces.apis.import_settings.triggers import ImportSettingsTrigger
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.workspaces.utils import delete_cards_mapping_settings
from fyle_accounting_mappings.models import EmployeeMapping, Mapping, MappingSetting

from .helpers import schedule_or_delete_fyle_import_tasks
from .queue import (
    async_auto_create_expense_field_mapping,
    schedule_cost_centers_creation,
    schedule_fyle_attributes_creation,
)


@receiver(post_save, sender=Mapping)
def resolve_post_mapping_errors(sender, instance: Mapping, **kwargs):
    """
    Resolve errors after mapping is created
    """
    if instance.source_type in ('CATEGORY', 'TAX_GROUP'):
        error = Error.objects.filter(expense_attribute_id=instance.source_id).first()
        if error:
            error.is_resolved = True
            error.save()


@receiver(post_save, sender=EmployeeMapping)
def resolve_post_employees_mapping_errors(sender, instance: Mapping, **kwargs):
    """
    Resolve errors after mapping is created
    """
    error = Error.objects.filter(
        expense_attribute_id=instance.source_employee_id
    ).first()
    if error:
        error.is_resolved = True
        error.save()


@receiver(post_save, sender=MappingSetting)
def run_post_mapping_settings_triggers(sender, instance: MappingSetting, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(
        workspace_id=instance.workspace_id
    ).first()

    if instance.source_field == 'PROJECT':
        schedule_or_delete_fyle_import_tasks(workspace_general_settings)

    if instance.source_field == 'COST_CENTER':
        schedule_cost_centers_creation(
            instance.import_to_fyle, int(instance.workspace_id)
        )

    if instance.is_custom:
        schedule_fyle_attributes_creation(int(instance.workspace_id))

    if workspace_general_settings:
        delete_cards_mapping_settings(workspace_general_settings)

    if instance.destination_field == 'DEPARTMENT':
        # add_department_grouping() doesn't require workspace_general_settings and mapping_settings, hence sending them as None
        trigger: ImportSettingsTrigger = ImportSettingsTrigger(
            workspace_general_settings=None,
            mapping_settings=None,
            workspace_id=instance.workspace_id,
        )
        trigger.add_department_grouping(instance.source_field)


@receiver(pre_save, sender=MappingSetting)
def run_pre_mapping_settings_triggers(sender, instance: MappingSetting, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    default_attributes = [
        'CATEGORY',
        'PROJECT',
        'COST_CENTER',
        'TAX_GROUP',
        'CORPORATE_CARD',
    ]

    instance.source_field = instance.source_field.upper().replace(' ', '_')

    if instance.source_field not in default_attributes:
        upload_attributes_to_fyle(
            workspace_id=int(instance.workspace_id),
            qbo_attribute_type=instance.destination_field,
            fyle_attribute_type=instance.source_field,
            source_placeholder=instance.source_placeholder,
        )

        async_auto_create_expense_field_mapping(instance)


@receiver(post_delete, sender=MappingSetting)
def run_post_delete_mapping_settings_triggers(
    sender, instance: MappingSetting, **kwargs
):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    if instance.destination_field == 'DEPARTMENT':
        # remove_department_grouping() doesn't require workspace_general_settings and mapping_settings, hence sending them as None
        trigger: ImportSettingsTrigger = ImportSettingsTrigger(
            workspace_general_settings=None,
            mapping_settings=None,
            workspace_id=instance.workspace_id,
        )
        trigger.remove_department_grouping(instance.source_field.lower())
