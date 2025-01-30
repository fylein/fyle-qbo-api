"""
Fyle Signals
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from fyle_accounting_mappings.models import DestinationAttribute, EmployeeMapping
from pydantic import ValidationError

from apps.fyle.models import ExpenseFilter
from apps.quickbooks_online.queue import async_run_post_configration_triggers
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from apps.workspaces.utils import delete_cards_mapping_settings


@receiver(post_save, sender=ExpenseFilter)
def run_post_save_expense_filters(sender, instance: ExpenseFilter, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    try:
        run_post_save_expense_filters(instance)
    except Exception as e:
        raise ValidationError(e)
