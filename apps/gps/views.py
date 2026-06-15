from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ActualizacionGPSSerializer
from seguridad.models import Bitacora

class RecepcionGPSView(APIView):
    """
    Entry Point Externo: API para recibir coordenadas.
    Control OWASP: Autenticación obligatoria por Token.
    """
    permission_classes = [IsAuthenticated] # Bloquea acceso sin Token

    def post(self, request):
        serializer = ActualizacionGPSSerializer(data=request.data)
        
        if serializer.is_valid():
            gps_record = serializer.save()
            
            # Auditoría: Registramos el evento exitoso
            Bitacora.objects.create(
                usuario=request.user,
                nombre_usuario=request.user.username,
                rol="Sistema Camión",
                accion="Actualización GPS",
                resultado="EXITOSO",
                descripcion=f"Coordenadas recibidas para el camión {gps_record.camion.placa}",
                direccion_ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
            )
            return Response({"mensaje": "Ubicación registrada de forma segura."}, status=status.HTTP_201_CREATED)
        
        # Auditoría: Registramos el intento fallido
        Bitacora.objects.create(
            usuario=request.user,
            nombre_usuario=request.user.username,
            rol="Sistema Camión",
            accion="Actualización GPS",
            resultado="RECHAZADO",
            descripcion="Intento de inyección de coordenadas con formato inválido.",
            direccion_ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)