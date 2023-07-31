import logging

from fyle.platform.exceptions import NoPrivilegeError
from qbosdk.exceptions import InvalidTokenError, WrongParamsError
from rest_framework.response import Response
from rest_framework.views import status

from apps.fyle.models import ExpenseGroup
from apps.mappings.models import GeneralMapping
from apps.workspaces.models import FyleCredential, QBOCredential, Workspace, WorkspaceGeneralSettings, WorkspaceSchedule

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_view_exceptions():
    def decorator(func):
        def new_fn(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ExpenseGroup.DoesNotExist:
                return Response(data={'message': 'Expense group not found'}, status=status.HTTP_400_BAD_REQUEST)

            except FyleCredential.DoesNotExist:
                return Response(data={'message': 'Fyle credentials not found in workspace'}, status=status.HTTP_400_BAD_REQUEST)

            except GeneralMapping.DoesNotExist:
                return Response({'message': 'General mappings do not exist for the workspace'}, status=status.HTTP_400_BAD_REQUEST)

            except WrongParamsError as exception:
                logger.info('QBO token expired workspace_id - %s %s', kwargs['workspace_id'], {'error': exception.response})
                return Response(data={'message': 'QBO token expired workspace_id'}, status=status.HTTP_400_BAD_REQUEST)

            except NoPrivilegeError as exception:
                logger.info('Invalid Fyle Credentials / Admin is disabled  for workspace_id%s %s', kwargs['workspace_id'], {'error': exception.response})
                return Response(data={'message': 'Invalid Fyle Credentials / Admin is disabled'}, status=status.HTTP_400_BAD_REQUEST)

            except InvalidTokenError as exception:
                logger.info('QBO token expired workspace_id - %s %s', kwargs['workspace_id'], {'error': exception.response})
                return Response(data={'message': 'QBO token expired workspace_id'}, status=status.HTTP_400_BAD_REQUEST)

            except Workspace.DoesNotExist:
                return Response(data={'message': 'Workspace with this id does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            except WorkspaceSchedule.DoesNotExist:
                return Response(data={'message': 'Workspace schedule does not exist in workspace'}, status=status.HTTP_400_BAD_REQUEST)

            except WorkspaceGeneralSettings.DoesNotExist:
                return Response({'message': 'General Settings does not exist in workspace'}, status=status.HTTP_400_BAD_REQUEST)

            except QBOCredential.DoesNotExist:
                logger.info('QBO credentials not found in workspace')
                return Response(data={'message': 'QBO credentials not found in workspace'}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as exception:
                logger.exception(exception)
                return Response(data={'message': 'An unhandled error has occurred, please re-try later'}, status=status.HTTP_400_BAD_REQUEST)

        return new_fn

    return decorator
