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
    CategoryView, CostCenterView, ProjectView, UserProfileView, ExpenseFieldsView, ExpenseCustomFieldsView, \
    ExpenseGroupSettingsView, RefreshFyleDimensionView, SyncFyleDimensionView, TaxGroupsView

urlpatterns = [
    path('user/', UserProfileView.as_view()),
    path('expense_groups/', ExpenseGroupView.as_view()),
    path('expense_group_settings/', ExpenseGroupSettingsView.as_view()),
    path('expense_groups/trigger/', ExpenseGroupScheduleView.as_view()),
    path('expense_groups/<int:expense_group_id>/', ExpenseGroupByIdView.as_view()),
    path('expense_groups/<int:expense_group_id>/expenses/', ExpenseView.as_view()),
    path('employees/', EmployeeView.as_view()),
    path('categories/', CategoryView.as_view()),
    path('cost_centers/', CostCenterView.as_view()),
    path('projects/', ProjectView.as_view()),
    path('expense_custom_fields/', ExpenseCustomFieldsView.as_view()),
    path('expense_fields/', ExpenseFieldsView.as_view()),
    path('sync_dimensions/', SyncFyleDimensionView.as_view()),
    path('refresh_dimensions/', RefreshFyleDimensionView.as_view()),
    path('tax_groups/', TaxGroupsView.as_view()),
]
