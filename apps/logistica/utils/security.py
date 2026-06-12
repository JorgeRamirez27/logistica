import logging
from django.utils.html import escape

logger = logging.getLogger('logistica.security')

def registrar_evento_bitacora(usuario, rol, accion, resultado, descripcion=""):
    mensaje = f"User: {usuario} | Role: {rol} | Action: {accion} | Status: {resultado} | Detail: {descripcion}"
    
    if resultado == "Rechazado":
        logger.warning(mensaje)
    else:
        logger.info(mensaje)

def sanitizar_texto(texto):
    if not texto:
        return ""
    return escape(texto.strip())