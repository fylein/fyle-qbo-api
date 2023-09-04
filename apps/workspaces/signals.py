"""
Workspace Signals
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping

from apps.fyle.queue import async_post_accounting_export_summary
from apps.quickbooks_online.queue import async_run_post_configration_triggers
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings, LastExportDetail
from apps.workspaces.utils import delete_cards_mapping_settings


@receiver(post_save, sender=WorkspaceGeneralSettings)
def run_post_configration_triggers(sender, instance: WorkspaceGeneralSettings, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    async_run_post_configration_triggers(instance)

    delete_cards_mapping_settings(instance)


# This is a manually triggered function
def post_delete_qbo_connection(workspace_id):
    """
    Post delete qbo connection
    :return: None
    """
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.onboarding_state in ('CONNECTION', 'MAP_EMPLOYEES', 'EXPORT_SETTINGS'):
        EmployeeMapping.objects.filter(workspace_id=workspace_id).delete()
        DestinationAttribute.objects.filter(workspace_id=workspace_id).delete()
        workspace.onboarding_state = 'CONNECTION'
        workspace.qbo_realm_id = None
        workspace.save()


@receiver(post_save, sender=LastExportDetail)
def run_post_save_last_export_detail(sender, instance: LastExportDetail, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    async_post_accounting_export_summary(instance.workspace.fyle_org_id, instance.workspace.id)
