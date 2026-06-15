from django.db import models
from django.core.validators import RegexValidator

class Cliente(models.Model):
    # Validación: Formato alfanumérico estricto
    validador_id = RegexValidator(
        regex=r'^[A-Z0-9]{5,15}$',
        message="El identificador debe ser alfanumérico en mayúsculas, entre 5 y 15 caracteres."
    )
    identificador = models.CharField(max_length=15, unique=True, validators=[validador_id])
    nombre = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50, blank=True, null=True)
    
    # Django previene inyecciones y valida el formato de correo automáticamente
    correo = models.EmailField(max_length=100)
    
    # Validación: Teléfono a 10 dígitos exactos
    validador_telefono = RegexValidator(
        regex=r'^\d{10}$',
        message="El teléfono debe contener exactamente 10 dígitos numéricos."
    )
    telefono = models.CharField(max_length=10, validators=[validador_telefono])
    
    # Auditoría: Campos gestionados 100% por el sistema
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.identificador} - {self.nombre} {self.apellido_paterno}"


class Direccion(models.Model):
    # ==========================================
    # RELACIÓN AÑADIDA: Vinculación estricta al propietario
    # ==========================================
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones')

    TIPO_CHOICES = [
        ('ORIGEN', 'Origen / Recolección'),
        ('DESTINO', 'Destino / Entrega'),
        ('RESGUARDO', 'Resguardo Interno'),
    ]

    validador_id_dir = RegexValidator(
        regex=r'^DIR-[0-9]{4,8}$',
        message="El identificador de dirección debe iniciar con 'DIR-' seguido de 4 a 8 números."
    )
    identificador = models.CharField(max_length=20, unique=True, validators=[validador_id_dir])
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=20)
    colonia = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    
    validador_cp = RegexValidator(
        regex=r'^\d{5}$',
        message="El código postal debe contener exactamente 5 dígitos."
    )
    codigo_postal = models.CharField(max_length=5, validators=[validador_cp])
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tipo}: {self.calle} {self.numero}, {self.ciudad}"