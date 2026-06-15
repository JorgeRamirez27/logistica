from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ActualizacionGPSSerializer
from seguridad.models import Bitacora
from apps.bienes.models import Bien # IMPORTANTE: Importa tu modelo Bien

class RecepcionGPSView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ActualizacionGPSSerializer(data=request.data)
        
        if serializer.is_valid():
            gps_record = serializer.save() # ¡Aquí se crea el objeto con el camion ya asignado!
            
            # Auditoría
            Bitacora.objects.create(
                usuario=request.user,
                nombre_usuario=request.user.username,
                rol="Sistema Camión",
                accion="Actualización GPS",
                resultado="EXITOSO",
                descripcion=f"Coordenadas recibidas para el camión {gps_record.placa_camion}",
                direccion_ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
            )
            return Response({"mensaje": "Ubicación registrada de forma segura."}, status=status.HTTP_201_CREATED)
        
        # Si el serializador falla, devuelve los errores automáticamente (ej: "Camión no encontrado")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)