from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ActualizacionGPSSerializer
from seguridad.models import Bitacora
from seguridad.views import obtener_ip
from apps.bienes.models import Bien # IMPORTANTE: Importa tu modelo Bien
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed

class RecepcionGPSView(APIView):
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        # Interceptamos errores de autenticación (Token inválido o ausente) antes de que DRF los devuelva
        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            Bitacora.objects.create(
                usuario=None,
                nombre_usuario="Dispositivo GPS (Anónimo)",
                rol="API Externa",
                accion="Recepción de coordenadas",
                resultado="RECHAZADO",
                descripcion=f"Intento de actualización rechazado: Token inválido o no proporcionado. Detalles: {str(exc)}",
                direccion_ip=obtener_ip(self.request) if hasattr(self, 'request') and self.request else "0.0.0.0"
            )
        return super().handle_exception(exc)

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
                direccion_ip=obtener_ip(request)
            )
            return Response({"mensaje": "Ubicación registrada de forma segura."}, status=status.HTTP_201_CREATED)
        
        # Si el serializador falla, formateamos y registramos los errores (ej. "Camión no encontrado")
        placa_enviada = request.data.get('placa_camion', request.data.get('placa', 'Desconocida'))
        errores_detalle = ", ".join([f"{k}: {v[0]}" for k, v in serializer.errors.items()])
        
        Bitacora.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            nombre_usuario=request.user.username if request.user.is_authenticated else "Dispositivo GPS",
            rol="Sistema Camión" if request.user.is_authenticated else "API Externa",
            accion="Actualización GPS",
            resultado="ERROR",
            descripcion=f"Intento de actualización fallido para placa '{placa_enviada}'. Motivo: {errores_detalle}",
            direccion_ip=obtener_ip(request)
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)