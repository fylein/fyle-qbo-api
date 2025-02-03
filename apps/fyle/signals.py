"""
Fyle Signals
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

from apps.fyle.models import ExpenseFilter
from apps.fyle.tasks import skip_expenses_pre_export


@receiver(post_save, sender=ExpenseFilter)
def run_post_save_expense_filters(sender, instance: ExpenseFilter, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    try:
        skip_expenses_pre_export(instance.workspace_id, instance)
    except Exception as e:
        raise ValidationError(f'Failed to process expense filter: {str(e)}') from e
