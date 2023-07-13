"""
Registering models in Django Admin
"""
from django.contrib import admin

from apps.tasks.models import TaskLog


admin.site.register(TaskLog)
