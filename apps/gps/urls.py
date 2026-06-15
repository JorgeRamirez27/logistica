from django.urls import path
from .views import RecepcionGPSView

app_name = 'gps'

urlpatterns = [
    path('actualizar/', RecepcionGPSView.as_view(), name='actualizar_gps'),
]