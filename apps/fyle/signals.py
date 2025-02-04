"""
Fyle Signals
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
import logging
from apps.fyle.models import ExpenseFilter
from apps.fyle.tasks import skip_expenses

logger = logging.getLogger(__name__)
logger.level = logging.INFO

@receiver(post_save, sender=ExpenseFilter)
def run_post_save_expense_filters(sender, instance: ExpenseFilter, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    if instance.join_by is None:
        try:
            skip_expenses(instance.workspace_id, instance)
        except Exception as e:
            logger.error('Error while processing expense filter for workspace_id: %s - %s', instance.workspace_id, str(e))
            raise ValidationError(f'Failed to process expense filter: {str(e)}') from e
