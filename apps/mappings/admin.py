"""
Registering models in Django Admin
"""
from django.contrib import admin

from apps.mappings.models import GeneralMapping

admin.site.register(GeneralMapping)
