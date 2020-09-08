"""
Registering models in Django Admin
"""
from django.contrib import admin

from .models import ExpenseGroup, Expense, ExpenseGroupSettings


admin.site.register(ExpenseGroup)
admin.site.register(ExpenseGroupSettings)
admin.site.register(Expense)
