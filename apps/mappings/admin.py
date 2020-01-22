"""
Registering models in Django Admin
"""
from django.contrib import admin

from .models import GeneralMapping, EmployeeMapping, CategoryMapping, ProjectMapping, CostCenterMapping


admin.site.register(GeneralMapping)
admin.site.register(EmployeeMapping)
admin.site.register(CategoryMapping)
admin.site.register(ProjectMapping)
admin.site.register(CostCenterMapping)
