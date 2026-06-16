import re
from django.core.exceptions import ValidationError

class ValidacionContrasenaRoles:
    def validate(self, password, user=None):
        errores = []
        
        # 1. Validaciones de complejidad exigida
        if not re.search(r'[A-Z]', password):
            errores.append("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r'[a-z]', password):
            errores.append("La contraseña debe contener al menos una letra minúscula.")
        if not re.search(r'\d', password):
            errores.append("La contraseña debe contener al menos un número.")
        if not re.search(r'[^A-Za-z0-9]', password):
            errores.append("La contraseña debe contener al menos un carácter especial (ej: @, $, !, %, *, ?, &).")
            
        # 2. Validación dinámica de la longitud según el rol
        min_length = 8 # Valor base para el Cliente
        
        if user:
            es_admin_o_supervisor = user.is_superuser or user.is_staff
            
            # Si el usuario ya está guardado y es supervisor
            if user.pk and user.groups.filter(name='Supervisor').exists():
                es_admin_o_supervisor = True
                
            if es_admin_o_supervisor:
                min_length = 10

        if len(password) < min_length:
            errores.append(f"Para tu tipo de perfil, la contraseña debe tener al menos {min_length} caracteres.")

        if errores:
            raise ValidationError(errores)

    def get_help_text(self):
        return "Tu contraseña debe tener al menos 8 caracteres (10 para supervisores/admins), e incluir una mayúscula, una minúscula, un número y un carácter especial."