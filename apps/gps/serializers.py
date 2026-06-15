from rest_framework import serializers
from .models import ActualizacionGPS, Camion

class ActualizacionGPSSerializer(serializers.ModelSerializer):
    placa_camion = serializers.CharField(write_only=True)

    class Meta:
        model = ActualizacionGPS
        fields = ['placa_camion', 'latitud', 'longitud', 'fecha_hora']
        read_only_fields = ['fecha_hora']

    def validate(self, data):
        """Sanitización y validación personalizada para la API"""
        placa = data.pop('placa_camion').upper().strip()
        try:
            camion = Camion.objects.get(placa=placa)
            data['camion'] = camion
        except Camion.DoesNotExist:
            raise serializers.ValidationError({"placa_camion": "Camión no encontrado o no registrado."})
        return data