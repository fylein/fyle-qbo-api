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

from apps.workspaces.apis.advanced_configurations.views import AdvancedConfigurationsView
from apps.workspaces.apis.errors.views import ErrorsView
from apps.workspaces.apis.export_settings.views import ExportSettingsView
from apps.workspaces.apis.import_settings.views import ImportSettingsView
from .clone_settings.views import CloneSettingsView
from apps.workspaces.apis.map_employees.views import MapEmployeesView

urlpatterns = [
    path('<int:workspace_id>/export_settings/', ExportSettingsView.as_view()),
    path('<int:workspace_id>/map_employees/', MapEmployeesView.as_view()),
    path('<int:workspace_id>/import_settings/', ImportSettingsView.as_view()),
    path('<int:workspace_id>/advanced_configurations/', AdvancedConfigurationsView.as_view()),
    path('<int:workspace_id>/clone_settings/', CloneSettingsView.as_view()),
    path('<int:workspace_id>/errors/', ErrorsView.as_view()),
]
