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

from .views import (
    CustomFieldView,
    ExpenseFieldsView,
    ExpenseFilterDeleteView,
    ExpenseFilterView,
    ExpenseGroupSettingsView,
    ExpenseGroupSyncView,
    ExpenseGroupView,
    ExpenseView,
    ExportableExpenseGroupsView,
    RefreshFyleDimensionView,
    SyncFyleDimensionView,
)

urlpatterns = [
    path('expense_groups/', ExpenseGroupView.as_view(), name='expense-groups'),
    path('exportable_expense_groups/', ExportableExpenseGroupsView.as_view(), name='exportable-expense-groups'),
    path('expense_group_settings/', ExpenseGroupSettingsView.as_view(), name='expense-group-settings'),
    path('expense_groups/sync/', ExpenseGroupSyncView.as_view(), name='sync-expense-groups'),
    path('expense_fields/', ExpenseFieldsView.as_view(), name='expense-fields'),
    path('sync_dimensions/', SyncFyleDimensionView.as_view(), name='sync-fyle-dimensions'),
    path('refresh_dimensions/', RefreshFyleDimensionView.as_view(), name='refresh-fyle-dimensions'),
    path('expense_filters/<int:pk>/', ExpenseFilterDeleteView.as_view(), name='expense-filters'),
    path('expense_filters/', ExpenseFilterView.as_view(), name='expense-filters'),
    path('expenses/', ExpenseView.as_view(), name='expenses'),
    path('custom_fields/', CustomFieldView.as_view(), name='custom-field'),
]
