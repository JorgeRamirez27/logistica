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

    def __str__(self):
        return f"{self.identificador} - {self.descripcion}"