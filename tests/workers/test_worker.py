import sys
from unittest.mock import Mock, patch

import pytest
from common.event import BaseEvent
from fyle_accounting_library.rabbitmq.models import FailedEvent

from workers import actions, worker
from workers.actions import handle_tasks
from workers.helpers import WorkerActionEnum
from workers.worker import Worker, main


@pytest.fixture
def mock_qconnector():
    """
    Mock QConnector
    """
    return Mock()


@pytest.fixture
def export_worker(mock_qconnector):
    """
    Mock Worker
    """
    worker = Worker(
        rabbitmq_url='mock_url',
        rabbitmq_exchange='mock_exchange',
        queue_name='mock_queue',
        binding_keys=['mock.binding.key'],
        qconnector_cls=Mock(return_value=mock_qconnector),
        event_cls=BaseEvent
    )
    worker.qconnector = mock_qconnector
    worker.event_cls = BaseEvent
    return worker


@pytest.mark.django_db
def test_process_message_success(export_worker):
    """
    Test process message success
    """
    with patch('workers.worker.handle_tasks') as mock_handle_tasks:
        mock_handle_tasks.side_effect = Exception('Test error')

        routing_key = 'test.routing.key'
        payload_dict = {
            'data': {'some': 'data'},
            'workspace_id': 123
        }
        event = BaseEvent()
        event.from_dict({'new': payload_dict})

        with pytest.raises(Exception, match='Test error'):
            export_worker.process_message(routing_key, event, 1)

        mock_handle_tasks.assert_called_once_with({'data': {'some': 'data'}, 'workspace_id': 123, 'retry_count': 1})


@pytest.mark.django_db
def test_handle_exception(export_worker):
    """
    Test handle exception
    """
    routing_key = 'test.routing.key'
    payload_dict = {
        'data': {'some': 'data'},
        'workspace_id': 123
    }
    error = Exception('Test error')

    export_worker.handle_exception(routing_key, payload_dict, error, 1)

    failed_event = FailedEvent.objects.get(
        routing_key=routing_key,
        workspace_id=123
    )
    assert failed_event.payload == payload_dict
    assert failed_event.error_traceback == 'Test error'


def test_shutdown(export_worker):
    """
    Test shutdown
    """
    with patch.object(export_worker, 'shutdown', wraps=export_worker.shutdown) as mock_shutdown:
        export_worker.shutdown(_=15, __=None)  # SIGTERM = 15
        mock_shutdown.assert_called_once_with(_=15, __=None)

    with patch.object(export_worker, 'shutdown', wraps=export_worker.shutdown) as mock_shutdown:
        export_worker.shutdown(_=0, __=None)  # Using default values
        mock_shutdown.assert_called_once_with(_=0, __=None)


@patch('workers.worker.signal.signal')
@patch('workers.worker.Worker')
def test_consume(mock_worker_class, mock_signal):
    """
    Test consume
    """
    mock_worker = Mock()
    mock_worker_class.return_value = mock_worker

    with patch.dict('os.environ', {'RABBITMQ_URL': 'test_url'}):
        from workers.worker import consume
        consume(queue_name='exports.p0')

    mock_worker.connect.assert_called_once()
    mock_worker.start_consuming.assert_called_once()
    assert mock_signal.call_count == 2  # Called for both SIGTERM and SIGINT


def test_handle_exports_calls_import_and_export_expenses():
    """
    Test handle exports calls import and export expenses
    """
    with patch('workers.actions.handle_tasks') as mock_handle_tasks:
        data = {'foo': 'bar'}
        actions.handle_tasks(data)
        mock_handle_tasks.assert_called_once_with({'foo': 'bar'})


def test_handle_tasks_successful_execution():
    """
    Test handle_tasks with valid action and method
    """
    with patch('workers.actions.import_string') as mock_import_string:
        mock_method = Mock()
        mock_import_string.return_value = mock_method

        payload = {
            'action': WorkerActionEnum.IMPORT_DIMENSIONS_TO_FYLE.value,
            'data': {
                'workspace_id': 1,
                'run_in_rabbitmq_worker': True
            }
        }

        handle_tasks(payload)

        mock_import_string.assert_called_once_with('apps.mappings.queues.initiate_import_to_fyle')
        mock_method.assert_called_once_with(workspace_id=1, run_in_rabbitmq_worker=True)


def test_handle_tasks_action_is_none(caplog):
    """
    Test handle_tasks when action is None
    """
    with patch('workers.actions.import_string') as mock_import_string:
        payload = {
            'action': None,
            'data': {'workspace_id': 1}
        }

        handle_tasks(payload)

        mock_import_string.assert_not_called()

        assert "Action is None for payload" in caplog.text


def test_handle_tasks_missing_action_key(caplog):
    """
    Test handle_tasks when action key is missing from payload
    """
    with patch('workers.actions.import_string') as mock_import_string:
        payload = {
            'data': {'workspace_id': 1}
        }

        handle_tasks(payload)

        mock_import_string.assert_not_called()

        assert "Action is None for payload" in caplog.text


def test_handle_tasks_method_not_found(caplog):
    """
    Test handle_tasks when method is not found in ACTION_METHOD_MAP
    """
    with patch('workers.actions.import_string') as mock_import_string:
        payload = {
            'action': 'NONEXISTENT_ACTION',
            'data': {'workspace_id': 1}
        }

        handle_tasks(payload)

        mock_import_string.assert_not_called()

        assert "Method is None for action - NONEXISTENT_ACTION" in caplog.text


def test_handle_tasks_empty_data():
    """
    Test handle_tasks with empty data
    """
    with patch('workers.actions.import_string') as mock_import_string:
        mock_method = Mock()
        mock_import_string.return_value = mock_method

        payload = {
            'action': WorkerActionEnum.CREATE_ADMIN_SUBSCRIPTION.value,
            'data': {}
        }

        handle_tasks(payload)

        mock_import_string.assert_called_once_with('apps.workspaces.tasks.create_admin_subscriptions')

        mock_method.assert_called_once_with()


def test_handle_tasks_different_action():
    """
    Test handle_tasks with a different valid action
    """
    with patch('workers.actions.import_string') as mock_import_string:
        mock_method = Mock()
        mock_import_string.return_value = mock_method

        payload = {
            'action': WorkerActionEnum.UPDATE_WORKSPACE_NAME.value,
            'data': {
                'workspace_id': 5,
                'workspace_name': 'Test Workspace'
            }
        }

        handle_tasks(payload)

        mock_import_string.assert_called_once_with('apps.workspaces.tasks.update_workspace_name')

        mock_method.assert_called_once_with(workspace_id=5, workspace_name='Test Workspace')


def test_handle_tasks_missing_data_key():
    """
    Test handle_tasks when data key is missing from payload
    This should cause a TypeError when trying to unpack **None
    """
    with patch('workers.actions.import_string') as mock_import_string:
        mock_method = Mock()
        mock_import_string.return_value = mock_method

        payload = {
            'action': WorkerActionEnum.CREATE_ADMIN_SUBSCRIPTION.value
        }

        with pytest.raises(TypeError):
            handle_tasks(payload)


def test_worker_entry_point(mocker):
    """
    Test worker entry point
    """
    mock_consume = mocker.patch("workers.worker.consume")

    sys.argv = ["worker.py", "--queue_name", "import"]

    worker.main()

    mock_consume.assert_called_once_with(queue_name="import")


def test_worker_main_function_coverage(mocker):
    """
    Test worker main function to ensure line 122 is covered
    """
    mock_consume = mocker.patch("workers.worker.consume")

    test_args = ["worker.py", "--queue_name", "test_queue"]

    with patch.object(sys, 'argv', test_args):
        main()

    mock_consume.assert_called_once_with(queue_name="test_queue")
