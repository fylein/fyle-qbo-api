from django.db import models
from django.contrib.postgres.fields import JSONField

from django_q.models import Schedule

from apps.workspaces.models import Workspace
from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.models import Bill


def get_default():
    return {
        'default': 'default value'
    }


class TaskLog(models.Model):
    """
    Table to store task logs
    """
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    type = models.CharField(max_length=50, help_text='Task type (FETCH_EXPENSES / CREATE_BILL)')
    task_id = models.CharField(max_length=255, null=True, help_text='Django Q task reference')
    expense_group = models.ForeignKey(ExpenseGroup, on_delete=models.PROTECT,
                                      null=True, help_text='Reference to Expense group')
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, help_text='Reference to Bill', null=True)
    status = models.CharField(max_length=255, help_text='Task Status')
    detail = JSONField(help_text='Task response', null=True, default=get_default)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')


class WorkspaceSchedule(models.Model):
    """
    Table to store Workspace Schedules
    """
    id = models.AutoField(primary_key=True)
    schedule = models.OneToOneField(Schedule, on_delete=models.PROTECT, help_text='Stores Fyle refresh token')
    task = models.ManyToManyField(TaskLog, help_text='Tasks under the Schedule')
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')
