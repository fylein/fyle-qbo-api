import logging

from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum

from apps.fyle.helpers import assert_valid_request
from workers.helpers import RoutingKeyEnum, WorkerActionEnum, publish_to_rabbitmq

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def async_import_and_export_expenses(body: dict, workspace_id: int) -> None:
    """
    Async'ly import and export expenses
    :param body: body
    :return: None
    """
    
    if body.get('data') and body['data'].get('org_id'):
        org_id = body['data']['org_id']
        assert_valid_request(workspace_id=workspace_id, fyle_org_id=org_id)

    if body.get('action') in ('ADMIN_APPROVED', 'APPROVED', 'STATE_CHANGE_PAYMENT_PROCESSING', 'PAID') and body.get('data'):
        report_id = body['data']['id']
        org_id = body['data']['org_id']
        state = body['data']['state']
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
    elif body.get('action') == 'ACCOUNTING_EXPORT_INITIATED' and body.get('data'):
        report_id = body['data']['id']
        org_id = body['data']['org_id']
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

    elif body.get('action') == 'UPDATED_AFTER_APPROVAL' and body.get('data') and body.get('resource') == 'EXPENSE':
        logger.info("| Updating non-exported expenses through webhook | Content: {WORKSPACE_ID: %s Payload: %s}", workspace_id, body.get('data'))
        payload = {
            'workspace_id': workspace_id,
            'action': WorkerActionEnum.EXPENSE_UPDATED_AFTER_APPROVAL.value,
            'data': {
                'data': body['data']
            }
        }
        publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.UTILITY.value)

    elif body.get('action') == 'EJECTED_FROM_REPORT' and body.get('data') and body.get('resource') == 'EXPENSE':
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

    elif body.get('action') == 'ADDED_TO_REPORT' and body.get('data') and body.get('resource') == 'EXPENSE':
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
