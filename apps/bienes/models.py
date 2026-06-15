from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from apps.clientes.models import Cliente, Direccion

class Bien(models.Model):
    ESTATUS_CHOICES = [
        ('REGISTRADO', 'Registrado'),
        ('EN_TRANSITO', 'En Tránsito'),
        ('ENTREGADO', 'Entregado'),
        ('INCIDENCIA', 'Con Incidencia'),
    ]

    validador_id_bien = RegexValidator(
        regex=r'^BN-[A-Z0-9]{6,10}$',
        message="El identificador debe iniciar con 'BN-' seguido de 6 a 10 caracteres alfanuméricos."
    )
    identificador = models.CharField(max_length=15, unique=True, validators=[validador_id_bien])
    descripcion = models.CharField(max_length=200)
    marca = models.CharField(max_length=50)
    
    # Seguridad: Bloquear valores negativos para evitar fallos de lógica de negocio
    valor = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='REGISTRADO')
    
    # Relaciones para trazabilidad
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='bienes')
    direccion_recoleccion = models.ForeignKey(Direccion, on_delete=models.RESTRICT, related_name='bienes_a_recolectar', null=True)
    direccion_entrega = models.ForeignKey(Direccion, on_delete=models.RESTRICT, related_name='bienes_a_entregar', null=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    placa = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    @property
    def viaje_activo(self):
        # Retorna el primer viaje que no esté finalizado
        return self.viajes.exclude(status='FINALIZADO').first()

    @property
    def ultima_posicion(self):
        # Validación de seguridad: si no hay placa, evitamos búsquedas erróneas
        if not self.placa:
            return None
            
        from apps.gps.models import ActualizacionGPS
        # Consulta optimizada usando el campo de texto desacoplado
        return ActualizacionGPS.objects.filter(placa_camion=self.placa).order_by('-fecha_hora').first()

    def __str__(self):
        return f"{self.identificador} - {self.descripcion}"
    def save(self, *args, **kwargs):
        # 1. Guardamos el Bien normalmente primero
        super().save(*args, **kwargs)
        
        # 2. Automatización del Viaje: Si el bien tiene ambas direcciones asignadas
        if self.direccion_recoleccion and self.direccion_entrega:
            viaje = self.viaje_activo
            
            # Convertimos las direcciones a texto (usando el formato que ya tienes en tu dropdown)
            texto_origen = str(self.direccion_recoleccion).lstrip(': ')
            texto_destino = str(self.direccion_entrega).lstrip(': ')
            
            if not viaje:
                # Si no hay viaje, lo creamos automáticamente
                Viaje.objects.create(
                    bien=self,
                    origen=texto_origen,
                    destino=texto_destino,
                    status='PROGRAMADO'
                )
            else:
                # Si ya hay un viaje activo, actualizamos las rutas por si el cliente las editó
                viaje.origen = texto_origen
                viaje.destino = texto_destino
                viaje.save()    
    
class Viaje(models.Model):
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='viajes')
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=[('PROGRAMADO', 'Programado'), ('EN_TRANSITO', 'En Tránsito'), ('FINALIZADO', 'Finalizado')],
        default='PROGRAMADO'
    )

    def __str__(self):
        return f"Viaje: {self.origen} a {self.destino} ({self.bien.placa})"