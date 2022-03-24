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

from .export_settings.views import ExportSettingsView
from .import_settings.views import ImportSettingsView
from .map_employees.views import MapEmployeesView

urlpatterns = [
    path('<int:workspace_id>/export_settings/', ExportSettingsView.as_view()),
    path('<int:workspace_id>/map_employees/', MapEmployeesView.as_view()),
    path('<int:workspace_id>/import_settings/', ImportSettingsView.as_view()),
]
