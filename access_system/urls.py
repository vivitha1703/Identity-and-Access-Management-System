"""
URL configuration for access_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from .views import auth_view, verify_view, landing_page, main_page, admin_dashboard, manager_dashboard, customer_dashboard, fetch_customers, add_customer, edit_customer, delete_customer
from .views import add_transaction, update_customer, fetch_manager, add_manager, update_manager, delete_manager, edit_manager, unlock_customer, generate_qr, verify_device, check_device_id
urlpatterns = [
    path('', landing_page, name='landing-page'),
    path('main/', main_page, name='main-page'),
    path('auth/', auth_view, name='auth-view'),
    path('verify/', verify_view, name='verify-view'),
    path('login/', auth_view, name='login-view'),
    path('api/customers/', fetch_customers, name='fetch_customers'),
    path('api/customers/add/', add_customer, name='add_customer'),
    path('api/customers/edit/<int:customer_id>/', edit_customer, name='edit_customer'),
    path('api/customers/update/<int:customer_id>/', update_customer, name='update_customer'),
    path('api/customers/delete/<int:customer_id>/', delete_customer, name='delete_customer'),
    path('fetch_manager/', fetch_manager, name='fetch_manager'),    
    path('api/managers/add/', add_manager, name='add_manager'),
    path('api/managers/update/<int:manager_id>/',update_manager, name='update_manager'),
    path('api/managers/delete/<int:manager_id>/',delete_manager, name='delete_manager'),
    path('edit_manager/<int:manager_id>/', edit_manager, name='edit_manager'),
    path('api/customers/unlock/<int:customer_id>/', unlock_customer, name='unlock-customer'),
    path('api/transactions/add/', add_transaction, name='add_transaction'),
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
    path('manager-dashboard/', manager_dashboard, name='manager-dashboard'),
    path('customer-dashboard/', customer_dashboard, name='customer-dashboard'),
    path('admin/', admin.site.urls),
    path('generate-qr/', generate_qr, name='generate_qr'),
    path('verify-device/', verify_device, name='verify_device'),
    path('check-device-id/', check_device_id, name='check_device_id'),  # New URL for checking device ID
]