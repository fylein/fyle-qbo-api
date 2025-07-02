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
from django.urls import include, path

from apps.quickbooks_online.urls import webhook_patterns
from apps.workspaces.views import (
    ConnectQBOView,
    ExportToQBOView,
    GeneralSettingsView,
    LastExportDetailView,
    ReadyView,
    SetupE2ETestView,
    TokenHealthView,
    WorkspaceAdminsView,
    WorkspaceView,
)

urlpatterns = [
    path('', WorkspaceView.as_view(), name='workspace'),
    path('<int:workspace_id>/', WorkspaceView.as_view(), name='workspace-by-id'),
    path('<int:workspace_id>/token_health/', TokenHealthView.as_view()),
    path('<int:workspace_id>/export_detail/', LastExportDetailView.as_view(), name='export-detail'),
    path('<int:workspace_id>/settings/general/', GeneralSettingsView.as_view(), name='workspace-general-settings'),
    path('<int:workspace_id>/connect_qbo/authorization_code/', ConnectQBOView.as_view()),
    path('<int:workspace_id>/credentials/qbo/', ConnectQBOView.as_view(), name='get-qbo-credentials'),
    path('<int:workspace_id>/exports/trigger/', ExportToQBOView.as_view(), name='export-to-qbo'),
    path('<int:workspace_id>/fyle/', include('apps.fyle.urls')),
    path('<int:workspace_id>/qbo/', include('apps.quickbooks_online.urls')),
    path('qbo/webhook_callback/', include(webhook_patterns)),
    path('<int:workspace_id>/mappings/', include('apps.mappings.urls')),
    path('<int:workspace_id>/tasks/', include('apps.tasks.urls')),
    path('<int:workspace_id>/admins/', WorkspaceAdminsView.as_view(), name='admin'),
    path('ready/', ReadyView.as_view(), name='ready'),
    path('<int:workspace_id>/setup_e2e_test/', SetupE2ETestView.as_view(), name='setup-e2e-test'),
]
