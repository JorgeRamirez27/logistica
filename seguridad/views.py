from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Bitacora

def obtener_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '0.0.0.0'))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    return ip

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=usuario, password=clave)
        
        if user is not None:
            auth_login(request, user)
            # Cumplimiento: Registro de inicio de sesión exitoso
            Bitacora.objects.create(
                usuario=user, nombre_usuario=user.username, rol="Autenticado",
                accion="Inicio de sesión", resultado="EXITOSO",
                descripcion="Autenticación validada en el sistema.", direccion_ip=obtener_ip(request)
            )
            return redirect('dashboard')
        else:
            # Cumplimiento: Registro de intento fallido
            Bitacora.objects.create(
                usuario=None, nombre_usuario=usuario, rol="Anónimo",
                accion="Inicio de sesión", resultado="RECHAZADO",
                descripcion="Credenciales inválidas proporcionadas.", direccion_ip=obtener_ip(request)
            )
            messages.error(request, 'Usuario o contraseña incorrectos.')
            
    return render(request, 'seguridad/login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    # El dashboard determinará qué botones mostrar basándose en el rol
    is_supervisor = request.user.groups.filter(name='Supervisor').exists() or request.user.is_superuser
    return render(request, 'seguridad/dashboard.html', {'is_supervisor': is_supervisor})

def landing_view(request):
    """
    Landing Page: Página de presentación pública del sistema.
    """
    return render(request, 'seguridad/landing.html')