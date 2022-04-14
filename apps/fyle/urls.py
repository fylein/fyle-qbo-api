"""fyle_qbo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from .views import ExpenseGroupView, ExpenseGroupByIdView, ExpenseGroupScheduleView, ExpenseView, EmployeeView, \
    CategoryView, CostCenterView, ProjectView, ExpenseFieldsView, ExpenseCustomFieldsView, ExportableExpenseGroupsView, \
    ExpenseGroupSettingsView, RefreshFyleDimensionView, SyncFyleDimensionView, ExpenseGroupCountView

urlpatterns = [
    path('expense_groups/', ExpenseGroupView.as_view(), name='expense-groups'),
    path('expense_groups/count/', ExpenseGroupCountView.as_view(), name='expense-groups-count'),
    path('exportable_expense_groups/', ExportableExpenseGroupsView.as_view(), name='exportable-expense-groups'),
    path('expense_group_settings/', ExpenseGroupSettingsView.as_view(), name='expense-group-settings'),
    path('expense_groups/trigger/', ExpenseGroupScheduleView.as_view()),
    path('expense_groups/<int:expense_group_id>/', ExpenseGroupByIdView.as_view(), name='expense-group-by-id'),
    path('expense_groups/<int:expense_group_id>/expenses/', ExpenseView.as_view(), name='expense-group-by-id-expenses'),
    path('employees/', EmployeeView.as_view(), name='employees'),
    path('categories/', CategoryView.as_view(), name='categories'),
    path('cost_centers/', CostCenterView.as_view(), name='cost-centers'),
    path('projects/', ProjectView.as_view(), name='projects'),
    path('expense_custom_fields/', ExpenseCustomFieldsView.as_view()),
    path('expense_fields/', ExpenseFieldsView.as_view(), name='expense-fields'),
    path('sync_dimensions/', SyncFyleDimensionView.as_view(), name='sync-fyle-dimensions'),
    path('refresh_dimensions/', RefreshFyleDimensionView.as_view(), name='refresh-fyle-dimensions'),
]
