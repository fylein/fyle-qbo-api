"""
Workspace Signals
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from apps.workspaces.utils import delete_cards_mapping_settings


@receiver(post_save, sender=WorkspaceGeneralSettings)
def run_post_configration_triggers(
    sender, instance: WorkspaceGeneralSettings, **kwargs
):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    async_task(
        "apps.quickbooks_online.tasks.async_sync_accounts", int(instance.workspace_id)
    )

    delete_cards_mapping_settings(instance)


# This is a manually triggered function
def post_delete_qbo_connection(workspace_id):
    """
    Post delete qbo connection
    :return: None
    """
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.onboarding_state in ("CONNECTION", "MAP_EMPLOYEES", "EXPORT_SETTINGS"):
        EmployeeMapping.objects.filter(workspace_id=workspace_id).delete()
        DestinationAttribute.objects.filter(workspace_id=workspace_id).delete()
        workspace.onboarding_state = "CONNECTION"
        workspace.qbo_realm_id = None
        workspace.save()
