"""
Registering models in Django Admin
"""
from django.contrib import admin

from .models import TaskLog


admin.site.register(TaskLog)
