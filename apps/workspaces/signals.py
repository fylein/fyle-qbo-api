"""
Workspace Signals
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import QBOCredential, WorkspaceGeneralSettings


@receiver(post_save, sender=WorkspaceGeneralSettings)
def run_post_configration_triggers(sender, instance: WorkspaceGeneralSettings, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    qbo_credentials: QBOCredential = QBOCredential.objects.get(workspace_id=int(instance.workspace_id))

    qbo_connection = QBOConnector(
        credentials_object=qbo_credentials,
        workspace_id=int(instance.workspace_id)
    )
    qbo_connection.sync_accounts()
