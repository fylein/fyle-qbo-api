import logging

from fyle_accounting_library.fyle_platform.enums import (
    ExpenseImportSourceEnum,
    WebhookAttributeActionEnum,
    WebhookCallbackActionEnum,
)

from apps.fyle.helpers import assert_valid_request
from apps.workspaces.models import FeatureConfig
from fyle_integrations_imports.modules.webhook_attributes import WebhookAttributeProcessor
from workers.helpers import RoutingKeyEnum, WorkerActionEnum, publish_to_rabbitmq

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_webhook_callback(body: dict, workspace_id: int) -> None:
    """
    Handle webhook callbacks for expenses and attributes
    :param body: webhook payload
    :param workspace_id: workspace id
    :return: None
    """
    action = body.get('action')
    resource = body.get('resource')
    data = body.get('data')
    org_id = data.get('org_id') if data else None
    assert_valid_request(workspace_id=workspace_id, fyle_org_id=org_id)

    if action in ('ADMIN_APPROVED', 'APPROVED', 'STATE_CHANGE_PAYMENT_PROCESSING', 'PAID') and data:
        report_id = data['id']
        state = data['state']
        payload = {
            'workspace_id': workspace_id,
            'action': WorkerActionEnum.EXPENSE_STATE_CHANGE.value,
            'data': {
                'report_id': report_id,
                'org_id': org_id,
                'is_state_change_event': True,
                'report_state': state,
                'imported_from': ExpenseImportSourceEnum.WEBHOOK
            }
        }
        publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.EXPORT_P0.value)
    elif action == 'ACCOUNTING_EXPORT_INITIATED' and data:
        report_id = data['id']
        payload = {
            'workspace_id': workspace_id,
            'action': WorkerActionEnum.DIRECT_EXPORT.value,
            'data': {
                'report_id': report_id,
                'org_id': org_id,
                'is_state_change_event': False,
                'report_state': None,
                'imported_from': ExpenseImportSourceEnum.DIRECT_EXPORT
            }
        }
        publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.EXPORT_P0.value)

    elif action == 'UPDATED_AFTER_APPROVAL' and data and resource == 'EXPENSE':
        logger.info("| Updating non-exported expenses through webhook | Content: {{WORKSPACE_ID: {} Payload: {}}}".format(workspace_id, data))
        payload = {
            'workspace_id': workspace_id,
            'action': WorkerActionEnum.EXPENSE_UPDATED_AFTER_APPROVAL.value,
            'data': {
                'data': data
            }
        }
        publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.UTILITY.value)

    elif action == 'EJECTED_FROM_REPORT' and data and resource == 'EXPENSE':
        expense_id = body['data']['id']
        logger.info("| Handling expense ejected from report | Content: {WORKSPACE_ID: %s EXPENSE_ID: %s Payload: %s}", workspace_id, expense_id, body.get('data'))
        payload = {
            'workspace_id': workspace_id,
            'action': WorkerActionEnum.EXPENSE_ADDED_EJECTED_FROM_REPORT.value,
            'data': {
                'expense_data': body['data'],
                'action_type': 'EJECTED_FROM_REPORT'
            }
        }
        publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.UTILITY.value)

    elif action == 'ADDED_TO_REPORT' and data and resource == 'EXPENSE':
        expense_id = body['data']['id']
        logger.info("| Handling expense added to report | Content: {WORKSPACE_ID: %s EXPENSE_ID: %s Payload: %s}", workspace_id, expense_id, body.get('data'))
        payload = {
            'workspace_id': workspace_id,
            'action': WorkerActionEnum.EXPENSE_ADDED_EJECTED_FROM_REPORT.value,
            'data': {
                'expense_data': body['data'],
                'action_type': 'ADDED_TO_REPORT'
            }
        }
        publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.UTILITY.value)

    elif (
        action == WebhookCallbackActionEnum.UPDATED.value
        and resource == 'ORG_SETTING'
    ):
        payload = {
            'workspace_id': workspace_id,
            'action': WorkerActionEnum.ORG_SETTING_UPDATED.value,
            'data': {
                'workspace_id': workspace_id,
                'org_settings': data
            }
        }
        publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.UTILITY.value)

    elif action in (WebhookAttributeActionEnum.CREATED, WebhookAttributeActionEnum.UPDATED, WebhookAttributeActionEnum.DELETED):
        try:
            fyle_webhook_sync_enabled = FeatureConfig.get_feature_config(workspace_id=workspace_id, key='fyle_webhook_sync_enabled')
            if fyle_webhook_sync_enabled:
                logger.info("| Processing attribute webhook | Content: {{WORKSPACE_ID: {} Payload: {}}}".format(workspace_id, body))
                processor = WebhookAttributeProcessor(workspace_id)
                processor.process_webhook(body)
        except Exception as e:
            logger.error(f"Error processing attribute webhook for workspace {workspace_id}: {str(e)}")
