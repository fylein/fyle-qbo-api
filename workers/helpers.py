from enum import Enum

from fyle_accounting_library.rabbitmq.connector import RabbitMQConnection
from fyle_accounting_library.rabbitmq.data_class import RabbitMQData
from fyle_accounting_library.rabbitmq.enums import RabbitMQExchangeEnum


class RoutingKeyEnum(str, Enum):
    """
    Routing key enum
    """
    IMPORT = 'IMPORT.*'
    UTILITY = 'UTILITY.*'
    EXPORT_P0 = 'EXPORT.P0.*'
    EXPORT_P1 = 'EXPORT.P1.*'


class WorkerActionEnum(str, Enum):
    """
    Worker action enum
    """
    DISABLE_ITEMS = 'IMPORT.DISABLE_ITEMS'
    SYNC_ACCOUNTS = 'IMPORT.SYNC_ACCOUNTS'
    DIRECT_EXPORT = 'EXPORT.P0.DIRECT_EXPORT'
    DASHBOARD_SYNC = 'EXPORT.P0.DASHBOARD_SYNC'
    CREATE_EXPENSE_GROUP = 'EXPORT.P1.CREATE_EXPENSE_GROUP'
    UPDATE_WORKSPACE_NAME = 'UTILITY.UPDATE_WORKSPACE_NAME'
    EXPENSE_STATE_CHANGE = 'EXPORT.P0.EXPENSE_STATE_CHANGE'
    ADD_ADMINS_TO_WORKSPACE = 'UTILITY.ADD_ADMINS_TO_WORKSPACE'
    SYNC_QUICKBOOKS_DIMENSION = 'IMPORT.SYNC_QUICKBOOKS_DIMENSION'
    IMPORT_DIMENSIONS_TO_FYLE = 'IMPORT.IMPORT_DIMENSIONS_TO_FYLE'
    CREATE_ADMIN_SUBSCRIPTION = 'UTILITY.CREATE_ADMIN_SUBSCRIPTION'
    TRIGGER_AUTO_MAP_EMPLOYEES = 'UTILITY.TRIGGER_AUTO_MAP_EMPLOYEES'
    BACKGROUND_SCHEDULE_EXPORT = 'EXPORT.P1.BACKGROUND_SCHEDULE_EXPORT'
    HANDLE_FYLE_REFRESH_DIMENSION = 'IMPORT.HANDLE_FYLE_REFRESH_DIMENSION'
    EXPENSE_UPDATED_AFTER_APPROVAL = 'UTILITY.EXPENSE_UPDATED_AFTER_APPROVAL'
    EXPENSE_ADDED_EJECTED_FROM_REPORT = 'UTILITY.EXPENSE_ADDED_EJECTED_FROM_REPORT'
    CHECK_INTERVAL_AND_SYNC_FYLE_DIMENSION = 'IMPORT.CHECK_INTERVAL_AND_SYNC_FYLE_DIMENSION'
    CHECK_INTERVAL_AND_SYNC_QUICKBOOKS_DIMENSION = 'IMPORT.CHECK_INTERVAL_AND_SYNC_QUICKBOOKS_DIMENSION'
    ORG_SETTING_UPDATED = 'UTILITY.ORG_SETTING_UPDATED'


QUEUE_BINDKEY_MAP = {
    'quickbooks_import': RoutingKeyEnum.IMPORT,
    'quickbooks_utility': RoutingKeyEnum.UTILITY,
    'quickbooks_export.p0': RoutingKeyEnum.EXPORT_P0,
    'quickbooks_export.p1': RoutingKeyEnum.EXPORT_P1
}


ACTION_METHOD_MAP = {
    WorkerActionEnum.DASHBOARD_SYNC: 'apps.workspaces.actions.export_to_qbo',
    WorkerActionEnum.SYNC_ACCOUNTS: 'apps.quickbooks_online.tasks.sync_accounts',
    WorkerActionEnum.DIRECT_EXPORT: 'apps.fyle.tasks.import_and_export_expenses',
    WorkerActionEnum.CREATE_EXPENSE_GROUP: 'apps.fyle.tasks.create_expense_groups',
    WorkerActionEnum.DISABLE_ITEMS: 'fyle_integrations_imports.tasks.disable_items',
    WorkerActionEnum.EXPENSE_STATE_CHANGE: 'apps.fyle.tasks.import_and_export_expenses',
    WorkerActionEnum.BACKGROUND_SCHEDULE_EXPORT: 'apps.workspaces.actions.export_to_qbo',
    WorkerActionEnum.UPDATE_WORKSPACE_NAME: 'apps.workspaces.tasks.update_workspace_name',
    WorkerActionEnum.HANDLE_FYLE_REFRESH_DIMENSION: 'apps.fyle.actions.refresh_fyle_dimension',
    WorkerActionEnum.IMPORT_DIMENSIONS_TO_FYLE: 'apps.mappings.queues.initiate_import_to_fyle',
    WorkerActionEnum.CREATE_ADMIN_SUBSCRIPTION: 'apps.workspaces.tasks.create_admin_subscriptions',
    WorkerActionEnum.TRIGGER_AUTO_MAP_EMPLOYEES: 'apps.mappings.actions.trigger_auto_map_employees',
    WorkerActionEnum.EXPENSE_UPDATED_AFTER_APPROVAL: 'apps.fyle.tasks.update_non_exported_expenses',
    WorkerActionEnum.EXPENSE_ADDED_EJECTED_FROM_REPORT: 'apps.fyle.tasks.handle_expense_report_change',
    WorkerActionEnum.ADD_ADMINS_TO_WORKSPACE: 'apps.workspaces.tasks.async_add_admins_to_workspace',
    WorkerActionEnum.CHECK_INTERVAL_AND_SYNC_FYLE_DIMENSION: 'apps.fyle.actions.sync_fyle_dimensions',
    WorkerActionEnum.SYNC_QUICKBOOKS_DIMENSION: 'apps.quickbooks_online.actions.refresh_quickbooks_dimensions',
    WorkerActionEnum.CHECK_INTERVAL_AND_SYNC_QUICKBOOKS_DIMENSION: 'apps.quickbooks_online.actions.sync_quickbooks_dimensions',
    WorkerActionEnum.ORG_SETTING_UPDATED: 'apps.fyle.tasks.handle_org_setting_updated'
}


def get_routing_key(queue_name: str) -> str:
    """
    Get the routing key for a given queue name
    :param queue_name: str
    :return: str
    """
    return QUEUE_BINDKEY_MAP.get(queue_name)


def publish_to_rabbitmq(payload: dict, routing_key: RoutingKeyEnum) -> None:
    """
    Publish messages to RabbitMQ
    :param: payload: dict
    :param: routing_key: RoutingKeyEnum
    :return: None
    """
    rabbitmq = RabbitMQConnection.get_instance(RabbitMQExchangeEnum.QBO_EXCHANGE)
    data = RabbitMQData(new=payload)
    rabbitmq.publish(routing_key, data)
