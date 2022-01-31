"""
Workspace Signals
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from apps.workspaces.models import WorkspaceGeneralSettings
from apps.workspaces.utils import delete_cards_mapping_settings


@receiver(post_save, sender=WorkspaceGeneralSettings)
def run_post_configration_triggers(sender, instance: WorkspaceGeneralSettings, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    async_task(
        'apps.quickbooks_online.tasks.async_sync_accounts',
        int(instance.workspace_id)
    )

    delete_cards_mapping_settings(instance)
