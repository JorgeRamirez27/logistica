from django.contrib import admin
from .models import Bien, Viaje

@admin.register(Bien)
class BienAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'descripcion', 'placa', 'estatus')

@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ('bien', 'origen', 'destino', 'status', 'fecha_inicio')
    list_filter = ('status',)