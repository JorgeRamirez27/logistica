from django.contrib import admin
from .models import Bitacora

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'accion', 'resultado', 'usuario', 'rol')
    list_filter = ('resultado', 'rol', 'accion')
    search_fields = ('accion', 'descripcion', 'nombre_usuario')
    
    # Hacer que todos los campos sean de solo lectura
    readonly_fields = [field.name for field in Bitacora._meta.fields]

    # Prevenir que se añadan registros desde el panel admin
    def has_add_permission(self, request):
        return False

    # Prevenir que se modifiquen registros
    def has_change_permission(self, request, obj=None):
        return False

    # Prevenir que se eliminen registros
    def has_delete_permission(self, request, obj=None):
        return False