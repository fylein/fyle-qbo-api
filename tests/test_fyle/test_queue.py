from django.core.cache import cache
from fyle_accounting_library.rabbitmq.data_class import Task

from apps.fyle.queue import handle_webhook_callback
from apps.quickbooks_online.queue import __create_chain_and_run
from apps.workspaces.models import FeatureConfig, Workspace


# This test is just for cov :D
def test_create_chain_and_run(mocker, db):
    mocker.patch('apps.quickbooks_online.queue.sync_fyle_dimensions')
    workspace_id = 3
    chain_tasks = [
        Task(
            target='apps.quickbooks_online.tasks.create_cheque',
            args=[1, 1, True, False]
        )
    ]

    __create_chain_and_run(workspace_id, chain_tasks, True)
    assert True


def test_create_chain_and_run_with_webhook_sync(mocker, db):
    """Test __create_chain_and_run skips dimension sync when webhook sync is enabled"""
    workspace = Workspace.objects.get(id=3)
    cache.clear()
    FeatureConfig.objects.update_or_create(
        workspace_id=workspace.id,
        defaults={'fyle_webhook_sync_enabled': True}
    )

    mock_sync = mocker.patch('apps.quickbooks_online.queue.sync_fyle_dimensions')
    chain_tasks = [
        Task(
            target='apps.quickbooks_online.tasks.create_cheque',
            args=[1, 1, True, False]
        )
    ]
    __create_chain_and_run(workspace.id, chain_tasks, True)
    mock_sync.assert_not_called()
    cache.clear()
    feature_config = FeatureConfig.objects.get(workspace_id=workspace.id)
    feature_config.fyle_webhook_sync_enabled = False
    feature_config.save()
    __create_chain_and_run(workspace.id, chain_tasks, True)
    mock_sync.assert_called_once_with(workspace.id)
    cache.clear()


# This test is just for cov :D
def test_handle_webhook_callback(db):
    body = {
        'action': 'ACCOUNTING_EXPORT_INITIATED',
        'data': {
            'id': 'rp1s1L3QtMpF',
            'org_id': 'or79Cob97KSh'
        }
    }

    handle_webhook_callback(body, 3)


# This test is just for cov :D (2)
def test_handle_webhook_callback_2(db):
    body = {
        'action': 'STATE_CHANGE_PAYMENT_PROCESSING',
        'data': {
            'id': 'rp1s1L3QtMpF',
            'org_id': 'or79Cob97KSh',
            'state': 'APPROVED'
        }
    }

    workspace, _ = Workspace.objects.update_or_create(
        fyle_org_id = 'or79Cob97KSh'
    )

    handle_webhook_callback(body, workspace.id)


def test_async_import_and_export_expenses_ejected_from_report(db):
    body = {
        'action': 'EJECTED_FROM_REPORT',
        'resource': 'EXPENSE',
        'data': {
            'id': 'txExpense123',
            'org_id': 'or79Cob97KSh'
        }
    }

    workspace = Workspace.objects.get(id=3)

    handle_webhook_callback(body, workspace.id)


def test_async_import_and_export_expenses_added_to_report(db):
    body = {
        'action': 'ADDED_TO_REPORT',
        'resource': 'EXPENSE',
        'data': {
            'id': 'txExpense456',
            'org_id': 'or79Cob97KSh',
            'report_id': 'rpReport123'
        }
    }

    workspace = Workspace.objects.get(id=3)

    handle_webhook_callback(body, workspace.id)
    handle_webhook_callback(body, workspace.id)


def test_handle_webhook_callback_attribute_webhooks(mocker, db):
    """Test attribute webhook processing with feature flag enabled and exception handling"""
    workspace = Workspace.objects.get(id=3)
    cache.clear()
    FeatureConfig.objects.update_or_create(
        workspace_id=workspace.id,
        defaults={'fyle_webhook_sync_enabled': True}
    )
    mock_processor = mocker.patch('apps.fyle.queue.WebhookAttributeProcessor')
    mock_processor_instance = mock_processor.return_value
    body = {
        'action': 'CREATED',
        'resource': 'CATEGORY',
        'data': {
            'id': 'cat123',
            'name': 'Travel',
            'org_id': 'or79Cob97KSh'
        }
    }
    handle_webhook_callback(body, workspace.id)
    mock_processor.assert_called_once_with(workspace.id)
    mock_processor_instance.process_webhook.assert_called_once_with(body)
    mock_processor_instance.process_webhook.side_effect = Exception('Test exception')
    body['action'] = 'UPDATED'
    handle_webhook_callback(body, workspace.id)
    assert mock_processor.call_count == 2
    cache.clear()
    feature_config = FeatureConfig.objects.get(workspace_id=workspace.id)
    feature_config.fyle_webhook_sync_enabled = False
    feature_config.save()
    body['action'] = 'DELETED'
    handle_webhook_callback(body, workspace.id)
    assert mock_processor.call_count == 2
    cache.clear()


def test_handle_webhook_callback_org_setting_updated(mocker, db):
    """
    Test handle_webhook_callback for ORG_SETTING UPDATED action
    """
    workspace = Workspace.objects.get(id=3)

    mock_publish_to_rabbitmq = mocker.patch('apps.fyle.queue.publish_to_rabbitmq')

    webhook_body = {
        'action': 'UPDATED',
        'resource': 'ORG_SETTING',
        'data': {
            'org_id': workspace.fyle_org_id,
            'regional_settings': {
                'locale': {
                    'date_format': 'DD/MM/YYYY',
                    'timezone': 'Asia/Kolkata'
                }
            }
        }
    }

    handle_webhook_callback(webhook_body, workspace.id)

    mock_publish_to_rabbitmq.assert_called_once()
    call_kwargs = mock_publish_to_rabbitmq.call_args[1]
    assert call_kwargs['payload']['workspace_id'] == workspace.id
    assert call_kwargs['payload']['action'] == 'UTILITY.ORG_SETTING_UPDATED'
    assert call_kwargs['payload']['data']['org_settings'] == webhook_body['data']
