"""
Mapping Signals
"""
import logging
from datetime import datetime, timedelta, timezone

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from fyle.platform.exceptions import WrongParamsError
from fyle_accounting_mappings.models import EmployeeMapping, Mapping, MappingSetting
from fyle_integrations_platform_connector import PlatformConnector
from rest_framework.exceptions import ValidationError

from apps.mappings.constants import GENERAL_MAPPING_ERROR_TYPES, SYNC_METHODS
from apps.mappings.models import GeneralMapping
from apps.quickbooks_online.utils import QBOConnector
from apps.tasks.models import Error
from apps.workspaces.apis.import_settings.triggers import ImportSettingsTrigger
from apps.workspaces.models import FyleCredential, QBOCredential, WorkspaceGeneralSettings
from apps.workspaces.utils import delete_cards_mapping_settings
from fyle_integrations_imports.models import ImportLog
from fyle_integrations_imports.modules.expense_custom_fields import ExpenseCustomField

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Mapping)
def resolve_post_mapping_errors(sender, instance: Mapping, **kwargs):
    """
    Resolve errors after mapping is created
    """
    if instance.source_type in ('CATEGORY'):
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
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=instance.workspace_id).first()

    if workspace_general_settings:
        delete_cards_mapping_settings(workspace_general_settings)

    if instance.destination_field == 'DEPARTMENT':
        # add_department_grouping() doesn't require workspace_general_settings and mapping_settings, hence sending them as None
        trigger: ImportSettingsTrigger = ImportSettingsTrigger(workspace_general_settings=None, mapping_settings=None, workspace_id=instance.workspace_id)
        trigger.add_department_grouping(instance.source_field)


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
        try:
            workspace_id = int(instance.workspace_id)
            # Checking is import_log exists or not if not create one
            import_log, is_created = ImportLog.objects.get_or_create(
                workspace_id=workspace_id,
                attribute_type=instance.source_field,
                defaults={
                    'status': 'IN_PROGRESS'
                }
            )

            last_successful_run_at = None
            if import_log and not is_created:
                last_successful_run_at = import_log.last_successful_run_at if import_log.last_successful_run_at else None
                time_difference = datetime.now() - timedelta(minutes=32)
                offset_aware_time_difference = time_difference.replace(tzinfo=timezone.utc)

                # if the import_log is present and the last_successful_run_at is less than 30mins then we need to update it
                # so that the schedule can run
                if last_successful_run_at and offset_aware_time_difference\
                    and (offset_aware_time_difference < last_successful_run_at):
                    import_log.last_successful_run_at = offset_aware_time_difference
                    last_successful_run_at = offset_aware_time_difference
                    import_log.save()

            qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
            qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

            # Creating the expense_custom_field object with the correct last_successful_run_at value
            expense_custom_field = ExpenseCustomField(
                workspace_id=workspace_id,
                source_field=instance.source_field,
                destination_field=instance.destination_field,
                sync_after=last_successful_run_at,
                sdk_connection=qbo_connection,
                destination_sync_methods=[SYNC_METHODS[instance.destination_field]]
            )

            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            platform = PlatformConnector(fyle_credentials=fyle_credentials)

            # setting the import_log status to IN_PROGRESS
            import_log.status = 'IN_PROGRESS'
            import_log.save()

            expense_custom_field.construct_payload_and_import_to_fyle(platform, import_log)
            expense_custom_field.sync_expense_attributes(platform)

            # NOTE: We are not setting the import_log status to COMPLETE
            # since the post_save trigger will run the import again in async manner

        except WrongParamsError as error:
            logger.error(
                'Error while creating %s workspace_id - %s in Fyle %s %s',
                instance.source_field, instance.workspace_id, error.message, {'error': error.response}
            )
            if error.response and 'message' in error.response:
                raise ValidationError({
                    'message': error.response['message'],
                    'field_name': instance.source_field
                })

        # setting the import_log.last_successful_run_at to -30mins for the post_save_trigger
        import_log = ImportLog.objects.filter(workspace_id=workspace_id, attribute_type=instance.source_field).first()
        if import_log.last_successful_run_at:
            last_successful_run_at = import_log.last_successful_run_at - timedelta(minutes=30)
            import_log.last_successful_run_at = last_successful_run_at
            import_log.save()


@receiver(post_save, sender=GeneralMapping)
def resolve_general_mapping_errors(sender, instance: GeneralMapping, **kwargs):
    """
    Resolve errors after general mapping is created
    """
    errors = Error.objects.filter(workspace_id=instance.workspace_id, is_resolved=False, error_type='GENERAL_MAPPING_ERROR')
    for error in errors:
        if error.error_detail in GENERAL_MAPPING_ERROR_TYPES:
            field_name = GENERAL_MAPPING_ERROR_TYPES[error.error_detail]
            field_value = getattr(instance, field_name)
            if field_value:
                error.is_resolved = True
                error.save()


@receiver(post_delete, sender=MappingSetting)
def run_post_delete_mapping_settings_triggers(sender, instance: MappingSetting, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    if instance.destination_field == 'DEPARTMENT':
        # remove_department_grouping() doesn't require workspace_general_settings and mapping_settings, hence sending them as None
        trigger: ImportSettingsTrigger = ImportSettingsTrigger(workspace_general_settings=None, mapping_settings=None, workspace_id=instance.workspace_id)
        trigger.remove_department_grouping(instance.source_field.lower())
