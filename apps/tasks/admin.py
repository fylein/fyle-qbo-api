"""
Registering models in Django Admin
"""
from django.contrib import admin

from .models import TaskLog, WorkspaceSchedule


admin.site.register(TaskLog)
admin.site.register(WorkspaceSchedule)
