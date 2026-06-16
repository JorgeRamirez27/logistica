from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from django.conf import settings

def is_supervisor(user):
    """Verifica si el usuario pertenece al grupo 'Supervisor' o es administrador."""
    return user.is_superuser or user.groups.filter(name='Supervisor').exists()

def supervisor_required(view_func):
    """
    Decorador para restringir el acceso solo a Supervisores.
    Si un Cliente intenta acceder, se le denegará el acceso (Error 403).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
            
        if is_supervisor(request.user):
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied("Acceso denegado: Esta sección es exclusiva para Supervisores.")
            
    return _wrapped_view