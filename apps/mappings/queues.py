from datetime import datetime

from django_q.models import Schedule
from fyle_accounting_mappings.models import MappingSetting

from apps.mappings.constants import SYNC_METHODS
from apps.mappings.models import GeneralMapping
from apps.workspaces.models import FeatureConfig, QBOCredential, WorkspaceGeneralSettings
from fyle_integrations_imports.dataclasses import TaskSetting
from fyle_integrations_imports.queues import chain_import_fields_to_fyle
from workers.helpers import RoutingKeyEnum, WorkerActionEnum, publish_to_rabbitmq


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


def schedule_auto_map_employees(employee_mapping_preference: str, workspace_id: int):
    if employee_mapping_preference:
        start_datetime = datetime.now()

        schedule, _ = Schedule.objects.update_or_create(func='apps.mappings.tasks.async_auto_map_employees', args='{0}'.format(workspace_id), defaults={'schedule_type': Schedule.MINUTES, 'minutes': 24 * 60, 'next_run': start_datetime})
    else:
        schedule: Schedule = Schedule.objects.filter(func='apps.mappings.tasks.async_auto_map_employees', args='{}'.format(workspace_id)).first()

        if schedule:
            schedule.delete()


def construct_tasks_and_chain_import_fields_to_fyle(workspace_id: int) -> None:
    """
    Initiate the Import of dimensions to Fyle
    :param workspace_id: Workspace Id
    :return: None

    Schedule will hit this func, if we want to process things via worker,
    we can publish to rabbitmq else chain it as usual.
    """
    feature_configs = FeatureConfig.objects.get(workspace_id=workspace_id)
    if feature_configs.import_via_rabbitmq:
        payload = {
            'workspace_id': workspace_id,
            'action': WorkerActionEnum.IMPORT_DIMENSIONS_TO_FYLE.value,
            'data': {
                'workspace_id': workspace_id,
                'run_in_rabbitmq_worker': True
            }
        }
        publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.IMPORT.value)
    else:
        initiate_import_to_fyle(workspace_id=workspace_id)


def initiate_import_to_fyle(workspace_id: int, run_in_rabbitmq_worker: bool = False) -> None:
    """
    Initiate import fields to Fyle
    :param workspace_id: Workspace Id
    :return: None
    """
    mapping_settings = MappingSetting.objects.filter(workspace_id=workspace_id, import_to_fyle=True)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    credentials = QBOCredential.objects.get(workspace_id=workspace_id)

    task_settings: TaskSetting = {
        'import_tax': None,
        'import_vendors_as_merchants': None,
        'import_categories': None,
        'import_items': None,
        'mapping_settings': [],
        'credentials': credentials,
        'sdk_connection_string': 'apps.quickbooks_online.utils.QBOConnector',
    }

    if workspace_general_settings.import_categories or workspace_general_settings.import_items:
        destination_sync_methods = []
        if workspace_general_settings.import_categories:
            destination_sync_methods.append(SYNC_METHODS['ACCOUNT'])
        if workspace_general_settings.import_items:
            destination_sync_methods.append(SYNC_METHODS['ITEM'])

        task_settings['import_categories'] = {
            'destination_field': 'ACCOUNT',
            'destination_sync_methods': destination_sync_methods,
            'is_auto_sync_enabled': True,
            'is_3d_mapping': False,
            'charts_of_accounts': workspace_general_settings.charts_of_accounts if 'accounts' in destination_sync_methods else None,
            'prepend_code_to_name': True if 'ACCOUNT' in workspace_general_settings.import_code_fields else False
        }

    if workspace_general_settings.import_tax_codes:
        task_settings['import_tax'] = {
            'destination_field': 'TAX_CODE',
            'destination_sync_methods': [SYNC_METHODS['TAX_CODE']],
            'is_auto_sync_enabled': False,
            'is_3d_mapping': False,
        }

    if workspace_general_settings.import_vendors_as_merchants:
        task_settings['import_vendors_as_merchants'] = {
            'destination_field': 'VENDOR',
            'destination_sync_methods': [SYNC_METHODS['VENDOR']],
            'is_auto_sync_enabled': True,
            'is_3d_mapping': False,
        }

    task_settings['import_items'] = workspace_general_settings.import_items

    if mapping_settings:
        for mapping_setting in mapping_settings:
            if mapping_setting.source_field in ['PROJECT', 'COST_CENTER'] or mapping_setting.is_custom:
                task_settings['mapping_settings'].append({
                    'source_field': mapping_setting.source_field,
                    'destination_field': mapping_setting.destination_field,
                    'destination_sync_methods': [SYNC_METHODS[mapping_setting.destination_field]],
                    'is_auto_sync_enabled': True,
                    'is_custom': mapping_setting.is_custom
                })

    chain_import_fields_to_fyle(
        workspace_id=workspace_id,
        task_settings=task_settings,
        run_in_rabbitmq_worker=run_in_rabbitmq_worker
    )
