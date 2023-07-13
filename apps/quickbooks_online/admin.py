"""
Registering models in Django Admin
"""
from django.contrib import admin

from apps.quickbooks_online.models import Bill, BillLineitem


admin.site.register(Bill)
admin.site.register(BillLineitem)
