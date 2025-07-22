import logging
import traceback

from fyle.platform.exceptions import InternalServerError, InvalidTokenError, RetryException, WrongParamsError
from qbosdk.exceptions import InvalidTokenError as QBOInvalidTokenError
from qbosdk.exceptions import WrongParamsError as QBOWrongParamsError

from apps.workspaces.models import QBOCredential
from fyle_integrations_imports.models import ImportLog
from fyle_qbo_api.utils import invalidate_qbo_credentials

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_import_exceptions(task_name):
    def decorator(func):
        def new_fn(workspace_id: int, *args):
            error = {'task': task_name, 'workspace_id': workspace_id, 'alert': False, 'message': None, 'response': None}
            try:
                return func(workspace_id, *args)
            except InvalidTokenError:
                error['message'] = 'Invalid Fyle refresh token'

            except QBOCredential.DoesNotExist:
                error['message'] = 'QBO credentials not found'

            except WrongParamsError as exception:
                error['message'] = exception.message
                error['response'] = exception.response
                error['alert'] = True

            except RetryException:
                error['message'] = 'Retrying task'

            except InternalServerError as exception:
                error['message'] = 'Internal server error while importing to Fyle'
                error['response'] = exception.__dict__

            except QBOWrongParamsError as exception:
                error['message'] = 'Something went wrong while importing to QBO workspace_id - {0}'.format(workspace_id)
                error['response'] = exception.__dict__

            except QBOInvalidTokenError as exception:
                error['message'] = 'QBO token expired'
                error['response'] = exception.__dict__
                invalidate_qbo_credentials(workspace_id)

            except Exception:
                response = traceback.format_exc()
                error['message'] = 'Something went wrong'
                error['response'] = response
                error['alert'] = True

            if error['alert']:
                logger.error(error)
            else:
                logger.info(error)

        return new_fn

    return decorator


def handle_import_exceptions_v2(func):
    def new_fn(expense_attribute_instance, *args):
        import_log: ImportLog = args[0]
        workspace_id = import_log.workspace_id
        attribute_type = import_log.attribute_type
        error = {
            'task': 'Import {0} to Fyle and Auto Create Mappings'.format(attribute_type),
            'workspace_id': workspace_id,
            'message': None,
            'response': None
        }
        try:
            return func(expense_attribute_instance, *args)
        except WrongParamsError as exception:
            error['message'] = exception.message
            error['response'] = exception.response
            error['alert'] = True
            import_log.status = 'FAILED'

        except InvalidTokenError:
            error['message'] = 'Invalid Token for fyle'
            error['alert'] = False
            import_log.status = 'FAILED'

        except InternalServerError:
            error['message'] = 'Internal server error while importing to Fyle'
            error['alert'] = True
            import_log.status = 'FAILED'

        except QBOWrongParamsError as exception:
            error['message'] = 'Something went wrong while importing to QBO workspace_id - {0}'.format(workspace_id)
            error['alert'] = False
            error['response'] = exception.__dict__
            import_log.status = 'FAILED'

        except (QBOInvalidTokenError, QBOCredential.DoesNotExist) as exception:
            error['message'] = 'Invalid Token or QBO credentials does not exist workspace_id - {0}'.format(workspace_id)
            error['alert'] = False
            error['response'] = exception.__dict__
            import_log.status = 'FAILED'
            invalidate_qbo_credentials(workspace_id)

        except Exception:
            response = traceback.format_exc()
            error['message'] = 'Something went wrong'
            error['response'] = response
            error['alert'] = False
            import_log.status = 'FATAL'

        if error['alert']:
            logger.error(error)
        else:
            logger.info(error)

        import_log.error_log = error
        import_log.save()

    return new_fn
