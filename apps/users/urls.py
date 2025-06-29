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

from apps.users.views import FyleOrgsView
from apps.workspaces.apis.clone_settings.views import CloneSettingsExistsView

urlpatterns = [
    path('orgs/', FyleOrgsView.as_view(), name='orgs'),
    path(
        'clone_settings/exists/',
        CloneSettingsExistsView.as_view()
    ),
]
