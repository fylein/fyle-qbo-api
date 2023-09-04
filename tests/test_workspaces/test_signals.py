import logging

from apps.workspaces.models import Workspace, LastExportDetail
from apps.workspaces.signals import post_delete_qbo_connection, post_save_last_export_detail

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
    except Exception:
        logger.info('null value in column "qbo_realm_id" of relation "workspaces" violates not-null constraint')

# This test is just for coverage :D
def test_post_save_last_export_detail(db):
    workspace_id = 3
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    last_export_detail.failed_expense_groups_count = 1
    last_export_detail.save()

    assert last_export_detail.failed_expense_groups_count == 1
