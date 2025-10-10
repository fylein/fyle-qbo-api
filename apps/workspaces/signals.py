"""
Workspace Signals
"""

from datetime import datetime, timezone

from django.core.cache import cache
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.quickbooks_online.queue import async_run_post_configration_triggers
from apps.workspaces.enums import CacheKeyEnum
from apps.workspaces.helpers import enable_multi_currency_support
from apps.workspaces.models import FeatureConfig, Workspace, WorkspaceGeneralSettings
from apps.workspaces.utils import delete_cards_mapping_settings
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping, ExpenseAttribute
from fyle_qbo_api.utils import patch_integration_settings_for_unmapped_cards


@receiver(pre_save, sender=WorkspaceGeneralSettings)
def pre_save_workspace_general_settings(sender, instance: WorkspaceGeneralSettings, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    old_instance = WorkspaceGeneralSettings.objects.filter(workspace_id=instance.workspace_id).first()
    if old_instance and old_instance.import_items == True and instance.import_items == False:
        DestinationAttribute.objects.filter(workspace_id=instance.workspace_id, attribute_type='ACCOUNT', display_name='Item', active=True).update(active=False, updated_at=datetime.now(tz=timezone.utc))


@receiver(post_save, sender=WorkspaceGeneralSettings)
def run_post_configration_triggers(sender, instance: WorkspaceGeneralSettings, created: bool, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    if created:
        enable_multi_currency_support(instance)

    async_run_post_configration_triggers(instance)

    delete_cards_mapping_settings(instance)

    if instance.corporate_credit_card_expenses_object in ('CREDIT CARD PURCHASE', 'DEBIT CARD EXPENSE'):
        unmapped_card_count = ExpenseAttribute.objects.filter(
            attribute_type="CORPORATE_CARD", workspace_id=instance.workspace_id, active=True, mapping__isnull=True
        ).count()
        patch_integration_settings_for_unmapped_cards(workspace_id=instance.workspace_id, unmapped_card_count=unmapped_card_count)
    else:
        patch_integration_settings_for_unmapped_cards(workspace_id=instance.workspace_id, unmapped_card_count=0)


@receiver(post_save, sender=FeatureConfig)
def invalidate_feature_config_cache(sender, instance: FeatureConfig, **kwargs):
    """
    Invalidate feature config cache when updated
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    cache_key = CacheKeyEnum.FEATURE_CONFIG.value.format(workspace_id=instance.workspace_id)
    cache.delete(cache_key)


# This is a manually triggered function
def post_delete_qbo_connection(workspace_id):
    """
    Post delete qbo connection
    :return: None
    """
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.onboarding_state in ('CONNECTION', 'EXPORT_SETTINGS'):
        EmployeeMapping.objects.filter(workspace_id=workspace_id).delete()
        DestinationAttribute.objects.filter(workspace_id=workspace_id).delete()
        workspace.onboarding_state = 'CONNECTION'
        workspace.qbo_realm_id = None
        workspace.save()
