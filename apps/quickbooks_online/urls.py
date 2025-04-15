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

from apps.quickbooks_online.views import (
    DestinationAttributesView,
    EmployeeView,
    QBOAttributesView,
    RefreshQuickbooksDimensionView,
    SearchedDestinationAttributesView,
    SyncQuickbooksDimensionView,
    VendorView,
    QBOFieldView
)

urlpatterns = [
    path('vendors/', VendorView.as_view()),
    path('employees/', EmployeeView.as_view()),
    path('sync_dimensions/', SyncQuickbooksDimensionView.as_view()),
    path('refresh_dimensions/', RefreshQuickbooksDimensionView.as_view()),
    path('destination_attributes/', DestinationAttributesView.as_view(), name='destination-attributes'),
    path('mapping_options/', SearchedDestinationAttributesView.as_view(), name='searching-destination-attributes'),
    path('qbo_attributes/', QBOAttributesView.as_view(), name='qbo-attributes'),
    path('fields/', QBOFieldView.as_view())
]
