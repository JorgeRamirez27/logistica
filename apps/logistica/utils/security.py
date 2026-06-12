import logging
from django.utils.html import escape

# Conectamos con el logger de la configuración global
logger = logging.getLogger('logistica.security')

def registrar_evento_bitacora(usuario, rol, accion, resultado, descripcion=""):
    """
    Capa de Seguridad: Bitácora y No Repudio
    Escribe una entrada estructurada en el archivo log.
    """
    mensaje = f"User: {usuario} | Role: {rol} | Action: {accion} | Status: {resultado} | Detail: {descripcion}"
    
    if resultado == "Rechazado":
        logger.warning(mensaje)
    else:
        logger.info(mensaje)

def sanitizar_texto(texto):
    """
    Capa de Seguridad: Sanitización inicial contra XSS
    Elimina espacios en blanco sobrantes y escapa caracteres especiales.
    """
    if not texto:
        return ""
    return escape(texto.strip())