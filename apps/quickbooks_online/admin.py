"""
Registering models in Django Admin
"""
from django.contrib import admin

from .models import Bill, BillLineitem


admin.site.register(Bill)
admin.site.register(BillLineitem)
