from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

class Camion(models.Model):
    """Entidad que representa el vehículo a rastrear."""
    validador_placa = RegexValidator(
        regex=r'^[A-Z0-9]{6,8}$',
        message="La placa debe ser alfanumérica, sin espacios, entre 6 y 8 caracteres."
    )
    placa = models.CharField(max_length=8, unique=True, validators=[validador_placa])
    descripcion = models.CharField(max_length=100)
    
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Camión {self.placa}"

class ActualizacionGPS(models.Model):
    """Registro inmutable de la ubicación de un camión en un momento dado."""
    placa_camion = models.CharField(max_length=8) 
    
    latitud = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitud = models.DecimalField(
        max_digits=10, 
        decimal_places=6,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )
    
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.placa_camion} -> {self.latitud}, {self.longitud}"