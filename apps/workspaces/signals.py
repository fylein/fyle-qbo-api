"""
Workspace Signals
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from apps.mappings.tasks import async_auto_map_employees, async_auto_map_ccc_account
from apps.mappings.models import GeneralMapping

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

    if instance.auto_map_employees:
        async_auto_map_employees(instance.workspace_id)

    general_mappings = GeneralMapping.objects.get(workspace_id=instance.workspace_id)
    if general_mappings.default_ccc_account_name:
        async_auto_map_ccc_account(instance.workspace_id)
