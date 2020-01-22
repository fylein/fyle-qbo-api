"""
Registering models in Django Admin
"""
from django.contrib import admin

from .models import ExpenseGroup, Expense


admin.site.register(ExpenseGroup)
admin.site.register(Expense)
