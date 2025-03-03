from unittest import mock
from fyle_integrations_imports.models import ImportLog
from fyle_integrations_imports.modules.projects import Project
from apps.workspaces.models import QBOCredential
from apps.quickbooks_online.utils import QBOConnector
from apps.mappings.exceptions import handle_import_exceptions_v2
from fyle.platform.exceptions import InternalServerError, InvalidTokenError, WrongParamsError
from qbosdk.exceptions import InvalidTokenError as QBOInvalidTokenError
from qbosdk.exceptions import WrongParamsError as QBOWrongParamsError


def test_handle_import_exceptions(mocker, db):

    mocked_patch = mock.MagicMock()
    mocker.patch('fyle_qbo_api.utils.patch_integration_settings', side_effect=mocked_patch)

    workspace_id = 3
    ImportLog.objects.create(
        workspace_id=workspace_id,
        status = 'IN_PROGRESS',
        attribute_type = 'PROJECT',
        total_batches_count = 10,
        processed_batches_count = 2,
        error_log = []
    )
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    import_log = ImportLog.objects.get(workspace_id=workspace_id, attribute_type='PROJECT')
    project = Project(workspace_id, 'CUSTOMER', None,  qbo_connection, 'customers', True)

    # WrongParamsError
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise WrongParamsError('This is WrongParamsError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'This is WrongParamsError'
    assert import_log.error_log['alert'] == True

    # FyleInvalidTokenError
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise InvalidTokenError('This is FyleInvalidTokenError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Invalid Token for fyle'
    assert import_log.error_log['alert'] == False

    # InternalServerError
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise InternalServerError('This is InternalServerError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Internal server error while importing to Fyle'
    assert import_log.error_log['alert'] == True

    # QBOWrongParamsError
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise QBOWrongParamsError('This is InternalServerError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Invalid Token or QBO credentials does not exist workspace_id - 3'
    assert import_log.error_log['alert'] == False
    args, kwargs = mocked_patch.call_args
    assert args[0] == workspace_id
    assert kwargs['is_token_expired'] == True

    # QBOInvalidTokenError
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise QBOInvalidTokenError('This is InternalServerError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Invalid Token or QBO credentials does not exist workspace_id - 3'
    assert import_log.error_log['alert'] == False
    args, kwargs = mocked_patch.call_args
    assert args[0] == workspace_id
    assert kwargs['is_token_expired'] == True

    # QBOCredential.DoesNotExist
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise QBOCredential.DoesNotExist('This is InternalServerError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Invalid Token or QBO credentials does not exist workspace_id - 3'
    assert import_log.error_log['alert'] == False

    # Exception
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise Exception('This is a general Exception')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FATAL'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Something went wrong'
    assert import_log.error_log['alert'] == False
