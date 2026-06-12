from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User, Group
from .forms import FormularioAltaBien
from .models import Bien, Direccion
from .utils.security import registrar_evento_bitacora

def vista_login(request):
    """
    Controlador simple de Login para estudiantes.
    Verifica credenciales y valida roles usando grupos de Django de manera directa.
    """
    error = None
    if request.method == "POST":
        usuario_txt = request.POST.get('username')
        clave_txt = request.POST.get('password')
        
        # Autenticación nativa
        user = authenticate(username=usuario_txt, password=clave_txt)
        
        if user is not None:
            auth_login(request, user)
            
            # Identificamos el rol verificando el grupo 'Supervisor' o si es administrador
            es_supervisor = user.groups.filter(name='Supervisor').exists() or user.is_superuser
            rol_actual = "Supervisor" if es_supervisor else "Cliente"
            
            # Guardamos el rol en la sesión para usarlo en los controles de acceso
            request.session['rol'] = rol_actual
            
            # Capa de Seguridad: Registro en Bitácora
            registrar_evento_bitacora(user.username, rol_actual, "Inicio de sesion", "Exitoso")
            
            if es_supervisor:
                return redirect('dashboard_supervisor')
            return redirect('mis_bienes')
        else:
            error = "Usuario o contraseña incorrectos."
            registrar_evento_bitacora(usuario_txt, "Desconocido", "Inicio de sesion", "Rechazado", "Credenciales invalidas")
            
    return render(request, 'logistica/login.html', {'error': error})


def vista_registrar_bien(request):
    """
    Caso de Uso: Registrar Bienes (Solo Clientes)
    """
    # Control de acceso manual al estilo de tus diapositivas de Autorización
    if not request.user.is_authenticated or request.session.get('rol') != 'Cliente':
        registrar_evento_bitacora(
            request.user.username if request.user.is_authenticated else "Anonimo", 
            request.session.get('rol', 'Ninguno'), 
            "Acceso alta de bien", 
            "Rechazado", 
            "Intento de acceso sin permisos"
        )
        return render(request, 'logistica/no_autorizado.html')

    form = FormularioAltaBien()
    
    if request.method == "POST":
        form = FormularioAltaBien(request.POST)
        if form.is_valid():
            # Capa de Persistencia Manual: Creamos las entidades paso a paso
            dir_rec = Direccion.objects.create(
                calle_numero=form.cleaned_data['rec_calle'],
                ciudad=form.cleaned_data['rec_ciudad'],
                estado=form.cleaned_data['rec_estado'],
                codigo_postal=form.cleaned_data['rec_cp']
            )
            
            dir_ent = Direccion.objects.create(
                calle_numero=form.cleaned_data['ent_calle'],
                ciudad=form.cleaned_data['ent_ciudad'],
                estado=form.cleaned_data['ent_estado'],
                codigo_postal=form.cleaned_data['ent_cp']
            )
            
            Bien.objects.create(
                usuario_id=request.user.id, # Amarrado al ID del usuario logueado
                descripcion=form.cleaned_data['descripcion'],
                valor=form.cleaned_data['valor'],
                direccion_recoleccion=dir_rec,
                direccion_entrega=dir_ent,
                estatus='pendiente'
            )
            
            registrar_evento_bitacora(request.user.username, "Cliente", "Alta de bien", "Exitoso", f"Registro el bien: {form.cleaned_data['descripcion']}")
            return redirect('mis_bienes')
        else:
            registrar_evento_bitacora(request.user.username, "Cliente", "Alta de bien", "Rechazado", "Formulario con datos invalidos")

    return render(request, 'logistica/registrar_bien.html', {'form': form})

def vista_mis_bienes(request):
    """
    Cascarón temporal para la pantalla de reportes del Cliente.
    """
    # Verificación de seguridad básica de sesión
    if not request.user.is_authenticated:
        return redirect('login')
        
    return render(request, 'logistica/cliente_bienes.html')


def vista_dashboard_supervisor(request):
    """
    Caso de Uso: Panel de Supervisión (Solo Supervisores)
    """
    # Control de acceso manual verificando la sesión
    if not request.user.is_authenticated or request.session.get('rol') != 'Supervisor':
        registrar_evento_bitacora(
            request.user.username if request.user.is_authenticated else "Anonimo", 
            request.session.get('rol', 'Ninguno'), 
            "Acceso dashboard supervisor", 
            "Rechazado", 
            "Intento de acceso sin permisos"
        )
        return render(request, 'logistica/no_autorizado.html')

    # Extracción de todos los bienes para supervisión
    todos_los_bienes = Bien.objects.all()

    # Lectura manual de la bitácora
    lineas_bitacora = []
    try:
        with open('bitacora_seguridad.log', 'r', encoding='utf-8') as archivo:
            todas_las_lineas = archivo.readlines()
            lineas_bitacora = todas_las_lineas[-50:]  # Extraemos solo las últimas 50 líneas
    except FileNotFoundError:
        lineas_bitacora = ["Aviso: El archivo bitacora_seguridad.log aún no existe o no ha sido creado."]

    return render(request, 'logistica/supervisor_dashboard.html', {'bienes': todos_los_bienes, 'bitacora': lineas_bitacora})