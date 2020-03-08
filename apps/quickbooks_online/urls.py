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

from .views import VendorView, AccountView, ClassView, DepartmentView, BillView, BillScheduleView, CustomerView

urlpatterns = [
    path('vendors/', VendorView.as_view({'get': 'get_vendors'})),
    path('accounts/', AccountView.as_view({'get': 'get_accounts'})),
    path('classes/', ClassView.as_view({'get': 'get_classes'})),
    path('departments/', DepartmentView.as_view({'get': 'get_departments'})),
    path('customers/', CustomerView.as_view({'get': 'get_customers'})),
    path('bills/', BillView.as_view()),
    path('bills/trigger/', BillScheduleView.as_view())
]
