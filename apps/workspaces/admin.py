"""
Registering models in Django Admin
"""
from django.contrib import admin

from .models import FyleCredential, QBOCredential, Workspace

admin.site.register(Workspace)
admin.site.register(FyleCredential)
admin.site.register(QBOCredential)
