from django.urls import path
from . import views

app_name = 'clientes' 

urlpatterns = [
   
    path('direcciones/registrar/', views.registrar_direccion, name='registrar_direccion'),
    # apps/clientes/urls.py
    path('direcciones/', views.listar_direcciones, name='listar_direcciones'),
    path('direcciones/<int:pk>/editar/', views.editar_direccion, name='editar_direccion'),
    path('direcciones/<int:pk>/eliminar/', views.eliminar_direccion, name='eliminar_direccion'),
]