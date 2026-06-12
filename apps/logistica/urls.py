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
from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # Si entran a la raíz, los redirigimos al login
    path('', lambda request: redirect('login'), name='raiz'),
    
    # Ruta para el Login simple
    path('login/', views.vista_login, name='login'),
    
    # Ruta para el formulario de captura del Cliente
    path('bienes/nuevo/', views.vista_registrar_bien, name='registrar_bien'),
    
    # --- NUEVAS RUTAS TEMPORALES PARA EVITAR EL ERROR ---
    path('bienes/mis-bienes/', views.vista_mis_bienes, name='mis_bienes'),
    path('supervisor/dashboard/', views.vista_dashboard_supervisor, name='dashboard_supervisor'),
]
