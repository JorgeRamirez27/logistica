"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from rest_framework.authtoken.views import obtain_auth_token
from seguridad import views as seguridad_views
from apps.clientes import views as clientes_views

urlpatterns = [
    # --- Landing Page (Raíz del sitio) ---
    path('', seguridad_views.landing_view, name='landing'),
    
    # --- Autenticación y Dashboard ---
    path('login/', seguridad_views.login_view, name='login'),
    path('logout/', seguridad_views.logout_view, name='logout'),
    path('dashboard/', seguridad_views.dashboard_view, name='dashboard'),
    
    # --- Panel de administración ---
    path('admin/', admin.site.urls),
    
    # --- Apps del sistema ---
    path('bienes/', include('apps.bienes.urls')),
    path('api/gps/', include('apps.gps.urls')),
    
    # --- API Auth ---
    path('api/token-auth/', obtain_auth_token, name='api_token_auth'),
    #path('clientes/direcciones/registrar/', clientes_views.registrar_direccion, name='registrar_direccion'),
    path('clientes/', include('apps.clientes.urls')),
]
