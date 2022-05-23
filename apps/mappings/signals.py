"""
Mapping Signals
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_q.tasks import async_task

from fyle_accounting_mappings.models import MappingSetting, Mapping, EmployeeMapping

from apps.tasks.models import Error
from apps.mappings.tasks import upload_attributes_to_fyle, schedule_cost_centers_creation,\
    schedule_fyle_attributes_creation, schedule_projects_creation
from apps.workspaces.utils import delete_cards_mapping_settings
from apps.workspaces.models import WorkspaceGeneralSettings


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
    error = Error.objects.filter(expense_attribute_id=instance.source_employee_id).first()
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
    if instance.source_field == 'PROJECT':
        schedule_projects_creation(instance.import_to_fyle, int(instance.workspace_id))

    if instance.source_field == 'COST_CENTER':
        schedule_cost_centers_creation(instance.import_to_fyle, int(instance.workspace_id))

    if instance.is_custom:
        schedule_fyle_attributes_creation(int(instance.workspace_id))

    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=instance.workspace_id).first()
    if workspace_general_settings:
        delete_cards_mapping_settings(workspace_general_settings)


@receiver(pre_save, sender=MappingSetting)
def run_pre_mapping_settings_triggers(sender, instance: MappingSetting, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    default_attributes = ['CATEGORY', 'PROJECT', 'COST_CENTER', 'TAX_GROUP', 'CORPORATE_CARD']

    instance.source_field = instance.source_field.upper().replace(' ', '_')

    if instance.source_field not in default_attributes:
        upload_attributes_to_fyle(
            workspace_id=int(instance.workspace_id),
            qbo_attribute_type=instance.destination_field,
            fyle_attribute_type=instance.source_field,
            source_placeholder=instance.source_placeholder,
        )

        async_task(
            'apps.mappings.tasks.auto_create_expense_fields_mappings',
            int(instance.workspace_id),
            instance.destination_field,
            instance.source_field
        )
