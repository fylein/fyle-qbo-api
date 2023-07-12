"""
Registering models in Django Admin
"""
from django.contrib import admin

from .models import Expense, ExpenseGroup, ExpenseGroupSettings

admin.site.register(ExpenseGroup)
admin.site.register(ExpenseGroupSettings)
admin.site.register(Expense)
