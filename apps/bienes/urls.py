# apps/bienes/urls.py
from django.urls import path
from . import views

app_name = 'bienes'

urlpatterns = [
    # Vistas de Cliente
    path('mis-bienes/', views.lista_bienes, name='lista_bienes'),
    path('registrar/', views.registrar_bien, name='registrar_bien'),
    path('editar/<int:pk>/', views.editar_bien, name='editar_bien'),
    
    # Vistas de Supervisor
    path('supervision/', views.supervision_general, name='supervision_general'),
    path('auditoria/', views.consulta_bitacora, name='consulta_bitacora'),
]