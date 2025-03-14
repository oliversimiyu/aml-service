"""
URL configuration for amlservice project.

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
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from core import views as core_views

urlpatterns = [
    # Main application views
    path('', login_required(core_views.dashboard), name='dashboard'),
    path('customers/', login_required(core_views.customer_list), name='customers'),
    path('transactions/', login_required(core_views.transaction_list), name='transactions'),
    path('documents/', login_required(core_views.document_list), name='documents'),
    path('risk-assessments/', login_required(core_views.risk_assessment_list), name='risk_assessments'),
    
    # Authentication views
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Admin and API URLs
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
