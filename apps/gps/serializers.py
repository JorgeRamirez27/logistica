from apps.bienes.models import Bien
from rest_framework import serializers
from .models import ActualizacionGPS, Camion

class ActualizacionGPSSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActualizacionGPS
        fields = ['placa_camion', 'latitud', 'longitud']

    def validate_placa_camion(self, value):
        # Validar que esta placa exista en la tabla Bienes
        if not Bien.objects.filter(placa=value.upper().strip()).exists():
            raise serializers.ValidationError("No existe un camión registrado con esta placa.")
        return value.upper().strip()