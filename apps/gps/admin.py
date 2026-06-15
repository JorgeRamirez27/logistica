from django.contrib import admin
from .models import Camion, ActualizacionGPS

admin.site.register(Camion)

@admin.register(ActualizacionGPS)
class ActualizacionGPSAdmin(admin.ModelAdmin):
    list_display = ('camion', 'latitud', 'longitud', 'fecha_hora')
    readonly_fields = ('fecha_hora',)