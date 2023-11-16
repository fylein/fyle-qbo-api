from datetime import datetime, timedelta

from django_q.models import Schedule
from django_q.tasks import async_task
from fyle_accounting_mappings.models import MappingSetting

from apps.mappings.models import GeneralMapping
from apps.workspaces.models import WorkspaceGeneralSettings, QBOCredential
from apps.mappings.helpers import get_auto_sync_permission
from fyle_integrations_imports.queues import chain_import_fields_to_fyle
from fyle_integrations_imports.helpers import TaskSettings

SYNC_METHODS = {
    'ACCOUNT': 'accounts',
    'ITEM': 'items',
    'VENDOR': 'vendors',
    'DEPARTMENT': 'departments',
    'TAX_CODE': 'tax_codes',
    'CLASS': 'classes',
    'CUSTOMER': 'customers',
}


def async_auto_create_expense_field_mapping(mapping_setting: MappingSetting):
    async_task('apps.mappings.tasks.auto_create_expense_fields_mappings', int(mapping_setting.workspace_id), mapping_setting.destination_field, mapping_setting.source_field)


def schedule_cost_centers_creation(import_to_fyle, workspace_id):
    if import_to_fyle:
        schedule, _ = Schedule.objects.update_or_create(func='apps.mappings.tasks.auto_create_cost_center_mappings', args='{}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': 24 * 60, 'next_run': datetime.now()})
    else:
        schedule: Schedule = Schedule.objects.filter(func='apps.mappings.tasks.auto_create_cost_center_mappings', args='{}'.format(workspace_id)).first()

        if schedule:
            schedule.delete()


def schedule_fyle_attributes_creation(workspace_id: int):
    mapping_settings = MappingSetting.objects.filter(is_custom=True, import_to_fyle=True, workspace_id=workspace_id).all()
    if mapping_settings:
        schedule, _ = Schedule.objects.get_or_create(
            func='apps.mappings.tasks.async_auto_create_custom_field_mappings', args='{0}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': 24 * 60, 'next_run': datetime.now() + timedelta(hours=24)}
        )
    else:
        schedule: Schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_create_custom_field_mappings', args='{0}'.format(workspace_id)).first()

        if schedule:
            schedule.delete()


def schedule_bill_payment_creation(sync_fyle_to_qbo_payments, workspace_id):
    general_mappings: GeneralMapping = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    if general_mappings:
        if sync_fyle_to_qbo_payments and general_mappings.bill_payment_account_id:
            start_datetime = datetime.now()
            schedule, _ = Schedule.objects.update_or_create(func='apps.quickbooks_online.tasks.create_bill_payment', args='{}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': 24 * 60, 'next_run': start_datetime})
    if not sync_fyle_to_qbo_payments:
        schedule: Schedule = Schedule.objects.filter(func='apps.quickbooks_online.tasks.create_bill_payment', args='{}'.format(workspace_id)).first()

        if schedule:
            schedule.delete()


def schedule_auto_map_ccc_employees(workspace_id: int):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    if general_settings.auto_map_employees and general_settings.corporate_credit_card_expenses_object != 'BILL':
        start_datetime = datetime.now()

        schedule, _ = Schedule.objects.update_or_create(func='apps.mappings.tasks.async_auto_map_ccc_account', args='{0}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': 24 * 60, 'next_run': start_datetime})
    else:
        schedule: Schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_map_ccc_account', args='{}'.format(workspace_id)).first()

        if schedule:
            schedule.delete()


def schedule_tax_groups_creation(import_tax_codes, workspace_id):
    if import_tax_codes:
        schedule, _ = Schedule.objects.update_or_create(func='apps.mappings.tasks.auto_create_tax_codes_mappings', args='{}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': 24 * 60, 'next_run': datetime.now()})
    else:
        schedule: Schedule = Schedule.objects.filter(func='apps.mappings.tasks.auto_create_tax_codes_mappings', args='{}'.format(workspace_id)).first()

        if schedule:
            schedule.delete()


def schedule_auto_map_employees(employee_mapping_preference: str, workspace_id: int):
    if employee_mapping_preference:
        start_datetime = datetime.now()

        schedule, _ = Schedule.objects.update_or_create(func='apps.mappings.tasks.async_auto_map_employees', args='{0}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': 24 * 60, 'next_run': start_datetime})
    else:
        schedule: Schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_map_employees', args='{}'.format(workspace_id)).first()

        if schedule:
            schedule.delete()


def async_disable_category_for_items_mapping(workspace_id: int):
    async_task('apps.mappings.tasks.disable_category_for_items_mapping', workspace_id)


def construct_tasks_and_chain_import_fields_to_fyle(workspace_id):
    """
    Chain import fields to Fyle
    :param workspace_id: Workspace Id
    """
    mapping_settings = MappingSetting.objects.filter(workspace_id=workspace_id, import_to_fyle=True)
    credentials = QBOCredential.objects.get(workspace_id=workspace_id)


    print("""

        construct_tasks_and_chain_import_fields_to_fyle
        
    """)

    task_settings: TaskSettings = {
        'import_tax': None,
        'import_vendors_as_merchants': None,
        'import_categories': None,
        'mapping_settings': [],
        'credentials': credentials,
        'sdk_connection_string': 'apps.quickbooks_online.utils.QBOConnector',
    }

    # For now we are only adding PROJECTS support that is why we are hardcoding it
    if mapping_settings:
        for mapping_setting in mapping_settings:
            if mapping_setting.source_field in ['PROJECT']:
                task_settings['mapping_settings'].append({
                    'source_field': mapping_setting.source_field,
                    'destination_field': mapping_setting.destination_field,
                    'destination_sync_method': SYNC_METHODS[mapping_setting.destination_field],
                    'is_auto_sync_enabled': get_auto_sync_permission(mapping_setting),
                    'is_custom': False,
                })

    chain_import_fields_to_fyle(workspace_id, task_settings)
