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
from django.urls import path, include

from .views import WorkspaceView, ReadyView, ConnectFyleView, ConnectQBOView, ScheduleView, GeneralSettingsView, \
    ScheduledSyncView

urlpatterns = [
    path('', WorkspaceView.as_view({'get': 'get', 'post': 'post'}), name='workspace'),
    path('<int:workspace_id>/', WorkspaceView.as_view({'get': 'get_by_id'}), name='workspace-by-id'),
    path('<int:workspace_id>/schedule/', ScheduleView.as_view({'post': 'post', 'get': 'get'}), name='workspace-schedule'),
    path('<int:workspace_id>/settings/general/', GeneralSettingsView.as_view({'post': 'post', 'get': 'get'}), name='workspace-general-settings'),
    path('<int:workspace_id>/schedule/trigger/', ScheduledSyncView.as_view({'post': 'post'})),
    path('<int:workspace_id>/connect_fyle/authorization_code/', ConnectFyleView.as_view({'post': 'post'})),
    path('<int:workspace_id>/credentials/fyle/', ConnectFyleView.as_view({'get': 'get'}), name='get-fyle-credentials'),
    path('<int:workspace_id>/credentials/fyle/delete/', ConnectFyleView.as_view({'post': 'delete'}), name='delete-fyle-credentials'),
    path('<int:workspace_id>/connect_qbo/authorization_code/', ConnectQBOView.as_view({'post': 'post'})),
    path('<int:workspace_id>/credentials/qbo/patch/', ConnectQBOView.as_view({'patch': 'patch'}), name='patch-qbo-credentials'),
    path('<int:workspace_id>/credentials/qbo/', ConnectQBOView.as_view({'get': 'get'}), name='get-qbo-credentials'),
    path('<int:workspace_id>/fyle/', include('apps.fyle.urls')),
    path('<int:workspace_id>/qbo/', include('apps.quickbooks_online.urls')),
    path('<int:workspace_id>/mappings/', include('apps.mappings.urls')),
    path('<int:workspace_id>/tasks/', include('apps.tasks.urls')),
    path('ready/', ReadyView.as_view({'get': 'get'}), name='ready')
]
