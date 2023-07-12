from datetime import datetime, timedelta
from django_q.tasks import async_task
from fyle_accounting_mappings.models import MappingSetting

from django_q.models import Schedule

from apps.mappings.models import GeneralMapping
from apps.workspaces.models import WorkspaceGeneralSettings


def async_auto_create_expense_field_mapping(mapping_setting: MappingSetting):
    async_task(
        'apps.mappings.tasks.auto_create_expense_fields_mappings',
        int(mapping_setting.workspace_id),
        mapping_setting.destination_field,
        mapping_setting.source_field,
    )


def schedule_cost_centers_creation(import_to_fyle, workspace_id):
    if import_to_fyle:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_cost_center_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now(),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_cost_center_mappings',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_fyle_attributes_creation(workspace_id: int):
    mapping_settings = MappingSetting.objects.filter(
        is_custom=True, import_to_fyle=True, workspace_id=workspace_id
    ).all()
    if mapping_settings:
        schedule, _ = Schedule.objects.get_or_create(
            func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
            args='{0}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now() + timedelta(hours=24),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
            args='{0}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_bill_payment_creation(sync_fyle_to_qbo_payments, workspace_id):
    general_mappings: GeneralMapping = GeneralMapping.objects.filter(
        workspace_id=workspace_id
    ).first()
    if general_mappings:
        if sync_fyle_to_qbo_payments and general_mappings.bill_payment_account_id:
            start_datetime = datetime.now()
            schedule, _ = Schedule.objects.update_or_create(
                func='apps.quickbooks_online.tasks.create_bill_payment',
                args='{}'.format(workspace_id),
                defaults={
                    'schedule_type': Schedule.MINUTES,
                    'minutes': 24 * 60,
                    'next_run': start_datetime,
                },
            )
    if not sync_fyle_to_qbo_payments:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.quickbooks_online.tasks.create_bill_payment',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_auto_map_ccc_employees(workspace_id: int):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    if (
        general_settings.auto_map_employees
        and general_settings.corporate_credit_card_expenses_object != 'BILL'
    ):
        start_datetime = datetime.now()

        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.async_auto_map_ccc_account',
            args='{0}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime,
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_map_ccc_account',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_tax_groups_creation(import_tax_codes, workspace_id):
    if import_tax_codes:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_tax_codes_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now(),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_tax_codes_mappings',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_auto_map_employees(employee_mapping_preference: str, workspace_id: int):
    if employee_mapping_preference:
        start_datetime = datetime.now()

        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.async_auto_map_employees',
            args='{0}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime,
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_map_employees',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def async_disable_category_for_items_mapping(workspace_id: int):
    async_task('apps.mappings.tasks.disable_category_for_items_mapping', workspace_id)
