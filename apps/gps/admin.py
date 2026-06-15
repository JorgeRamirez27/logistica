from django.contrib import admin
from .models import ActualizacionGPS, Camion

@admin.register(ActualizacionGPS)
class ActualizacionGPSAdmin(admin.ModelAdmin):
    # ¡Aquí estaba el error! Debe decir 'placa_camion', no 'camion'
    list_display = ('placa_camion', 'latitud', 'longitud', 'fecha_hora')

@admin.register(Camion)
class CamionAdmin(admin.ModelAdmin):
    list_display = ('placa', 'descripcion')