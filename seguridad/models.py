from django.db import models
from django.contrib.auth.models import User

class Bitacora(models.Model):
    RESULTADO_CHOICES = [
        ('EXITOSO', 'Exitoso'),
        ('RECHAZADO', 'Rechazado'),
        ('ERROR', 'Error del Sistema'),
    ]

    fecha_hora = models.DateTimeField(auto_now_add=True)
    # Puede ser nulo si el intento de acceso es de un usuario no registrado o el GPS
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_usuario = models.CharField(max_length=150, help_text="Para conservar el registro si el usuario es eliminado")
    rol = models.CharField(max_length=50)
    accion = models.CharField(max_length=100)
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES)
    descripcion = models.TextField()
    direccion_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        # La bitácora NUNCA debe ser modificada, solo se deben insertar registros
        verbose_name = 'Registro de Bitácora'
        verbose_name_plural = 'Registros de Bitácora'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.fecha_hora} | {self.accion} | {self.resultado}"