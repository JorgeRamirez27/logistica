from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from apps.clientes.models import Cliente

class IdentificadorClienteBackend(ModelBackend):
    """
    Permite iniciar sesión usando el 'identificador' del Cliente (ej: JORGE2026),
    o el 'username' clásico para los supervisores/admins.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        try:
            # 1. Buscamos si lo que ingresó el usuario es un identificador logístico
            cliente = Cliente.objects.get(identificador=username)
            
            # 2. Obtenemos el usuario de Django buscando el correo asociado a ese cliente
            try:
                user = User.objects.get(email=cliente.correo)
            except User.DoesNotExist:
                return None
                
        except Cliente.DoesNotExist:
            # 3. Si no es un cliente, intentamos buscarlo como un usuario normal (Admin/Supervisor)
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        # 4. Si encontramos al usuario (ya sea por cliente o admin), verificamos su contraseña
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None