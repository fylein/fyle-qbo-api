from apps.workspaces.signals import post_delete_qbo_connection
from apps.workspaces.models import Workspace
import logging

logger = logging.getLogger(__name__)


def test_post_delete_qbo_connection(db):
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    workspace.onboarding_state = 'EXPORT_SETTINGS'
    workspace.save()

    try:
        post_delete_qbo_connection(workspace_id)

        workspace = Workspace.objects.get(id=workspace_id)

        assert workspace.qbo_realm_id == None
    except:
        logger.info('null value in column "qbo_realm_id" of relation "workspaces" violates not-null constraint')
        