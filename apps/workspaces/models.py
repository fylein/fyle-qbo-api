"""
Workspace Models
"""
from django.db import models
from django.contrib.auth import get_user_model

from django_q.tasks import Schedule

User = get_user_model()


class Workspace(models.Model):
    """
    Workspace model
    """
    id = models.AutoField(primary_key=True, help_text='Unique Id to identify a workspace')
    name = models.CharField(max_length=255, help_text='Name of the workspace')
    user = models.ManyToManyField(User, help_text='Reference to users table')
    fyle_org_id = models.CharField(max_length=255, help_text='org id')
    qbo_realm_id = models.CharField(max_length=255, help_text='qbo realm id')
    last_synced_at = models.DateTimeField(help_text='Datetime when expenses were pulled last', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')


class WorkspaceSettings(models.Model):
    """
    Workspace Settings
    """
    id = models.AutoField(primary_key=True, help_text='Unique Id to identify a workspace settings')
    schedule_enabled = models.BooleanField(default=False)
    schedule = models.OneToOneField(Schedule, on_delete=models.PROTECT, null=True)
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')


class QBOCredential(models.Model):
    """
    Table to store QBO credentials
    """
    id = models.AutoField(primary_key=True)
    refresh_token = models.TextField(help_text='Stores QBO refresh token')
    realm_id = models.CharField(max_length=40, help_text='QBO realm / company Id')
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')


class FyleCredential(models.Model):
    """
    Table to store Fyle credentials
    """
    id = models.AutoField(primary_key=True)
    refresh_token = models.TextField(help_text='Stores Fyle refresh token')
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')
