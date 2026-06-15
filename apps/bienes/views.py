from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import BienForm
from .models import Bien
from apps.clientes.models import Cliente
from seguridad.models import Bitacora

def registrar_en_bitacora(request, accion, resultado, descripcion):
    """
    Función auxiliar transversal de la Capa de Seguridad.
    Garantiza la trazabilidad capturando la sesión, rol e IP del actor.
    """
    rol = "Anónimo"
    if request.user.is_authenticated:
        if request.user.is_superuser:
            rol = "Superusuario"
        elif request.user.groups.filter(name='Supervisor').exists():
            rol = "Supervisor"
        elif request.user.groups.filter(name='Cliente').exists():
            rol = "Cliente"
        else:
            rol = "Autenticado"
    
    # Captura segura de la IP del cliente (considerando proxies)
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()

    Bitacora.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        nombre_usuario=request.user.username if request.user.is_authenticated else "Anónimo",
        rol=rol,
        accion=accion,
        resultado=resultado,
        descripcion=descripcion,
        direccion_ip=ip
    )


@login_required
def lista_bienes(request):
    """
    Control: Aislamiento de datos a nivel de consulta.
    Garantiza que un cliente SOLO pueda listar sus propios bienes.
    """
    # Control de autorización por Rol
    if not request.user.groups.filter(name='Cliente').exists() and not request.user.is_superuser:
        # Si el rol es Supervisor, lo redirigimos a su espacio correspondiente
        if request.user.groups.filter(name='Supervisor').exists():
            return redirect('bienes:supervision_general')
        raise PermissionDenied("No tienes permisos para ver esta sección.")

    try:
        # Vinculamos al usuario de la sesión con su entidad Cliente por medio del correo
        cliente_perfil = Cliente.objects.get(correo=request.user.email)
        # Mitigación de exposición: Filtro estricto por propietario
        bienes = Bien.objects.filter(cliente=cliente_perfil)
    except Cliente.DoesNotExist:
        bienes = Bien.objects.none()

    return render(request, 'bienes/lista.html', {'bienes': bienes})


@login_required
def registrar_bien(request):
    """
    Entry Point: Alta de bienes.
    Control: Prevención de Mass Assignment mediante asignación forzada en backend.
    """
    if not request.user.groups.filter(name='Cliente').exists() and not request.user.is_superuser:
        registrar_en_bitacora(
            request, "Alta de bien", "RECHAZADO",
            f"Usuario '{request.user.username}' intentó acceder al formulario de alta sin el rol requerido."
        )
        raise PermissionDenied("Acceso denegado.")

    try:
        cliente_perfil = Cliente.objects.get(correo=request.user.email)
    except Cliente.DoesNotExist:
        registrar_en_bitacora(
            request, "Alta de bien", "ERROR",
            f"El usuario '{request.user.username}' no posee un perfil de Cliente asociado a su correo."
        )
        raise PermissionDenied("Tu cuenta de usuario no está vinculada a un perfil logístico de Cliente.")

    if request.method == 'POST':
        form = BienForm(request.POST)
        if form.is_valid():
            # commit=False nos permite interceptar el objeto antes de guardarlo en la BD
            bien = form.save(commit=False)
            # Control de seguridad: Forzamos el propietario desde la sesión, no desde el POST del cliente
            bien.cliente = cliente_perfil
            bien.save()

            registrar_en_bitacora(
                request, "Alta de bien", "EXITOSO",
                f"Bien '{bien.identificador}' creado correctamente por el cliente."
            )
            return redirect('bienes:lista_bienes')
        else:
            registrar_en_bitacora(
                request, "Alta de bien", "RECHAZADO",
                "Intento de registro fallido: el formulario contiene datos inválidos."
            )
    else:
        form = BienForm()

    return render(request, 'bienes/registrar.html', {'form': form})


@login_required
def editar_bien(request, pk):
    """
    Entry Point: Actualización de bienes.
    Control: Mitigación de IDOR forzando el parámetro 'cliente' en la búsqueda del objeto.
    """
    try:
        cliente_perfil = Cliente.objects.get(correo=request.user.email)
        # Control estricto: Si el bien con esa PK no le pertenece al cliente, Django arrojará un 404
        bien = get_object_or_404(Bien, pk=pk, cliente=cliente_perfil)
    except Cliente.DoesNotExist:
        registrar_en_bitacora(
            request, "Actualización de bienes", "RECHAZADO",
            f"Intento de alteración de bien ID {pk} por usuario sin perfil válido."
        )
        raise PermissionDenied()

    if request.method == 'POST':
        form = BienForm(request.POST, instance=bien)
        if form.is_valid():
            form.save()
            registrar_en_bitacora(
                request, "Actualización de bienes", "EXITOSO",
                f"Modificación del bien '{bien.identificador}' completada con éxito."
            )
            return redirect('bienes:lista_bienes')
        else:
            registrar_en_bitacora(
                request, "Actualización de bienes", "RECHAZADO",
                f"Fallo al actualizar bien '{bien.identificador}': datos inválidos."
            )
    else:
        form = BienForm(instance=bien)

    return render(request, 'bienes/editar.html', {'form': form, 'bien': bien})
# Asegúrate de importar Bitacora al inicio si no lo has hecho
# from seguridad.models import Bitacora

@login_required
def supervision_general(request):
    """
    Entry Point: Consulta general del supervisor.
    Control: Validación estricta de rol para evitar acceso indebido.
    """
    # 1. Control de Autorización: Validar que el usuario pertenezca al grupo 'Supervisor'
    is_supervisor = request.user.groups.filter(name='Supervisor').exists()
    
    if not is_supervisor and not request.user.is_superuser:
        # Registrar intento de acceso indebido (Trazabilidad y no repudio)
        registrar_en_bitacora(
            request, "Consulta general", "RECHAZADO",
            f"El usuario '{request.user.username}' intentó acceder al panel de supervisión sin privilegios."
        )
        raise PermissionDenied("Acceso exclusivo para personal de supervisión. No tienes el rol requerido.")

    # 2. Lectura global de datos: El supervisor ve TODOS los registros sin filtro de propietario
    # select_related optimiza la consulta SQL evitando inyecciones o sobrecargas
    bienes_totales = Bien.objects.all().select_related('cliente', 'direccion_recoleccion', 'direccion_entrega')
    
    # 3. Auditoría de la acción permitida
    registrar_en_bitacora(
        request, "Consulta general", "EXITOSO",
        f"El supervisor '{request.user.username}' consultó el listado global de bienes."
    )

    return render(request, 'bienes/supervision.html', {'bienes': bienes_totales})


@login_required
def consulta_bitacora(request):
    """
    Entry Point: Revisión de eventos del sistema por el supervisor.
    Apoya directamente la trazabilidad y el no repudio.
    """
    is_supervisor = request.user.groups.filter(name='Supervisor').exists()
    
    if not is_supervisor and not request.user.is_superuser:
        registrar_en_bitacora(
            request, "Consulta de bitácora", "RECHAZADO",
            f"Intento no autorizado de lectura de auditoría por '{request.user.username}'."
        )
        raise PermissionDenied("Solo el supervisor puede auditar la bitácora del sistema.")

    # Extraemos los últimos 100 eventos inmutables
    eventos = Bitacora.objects.all()[:100]

    registrar_en_bitacora(
        request, "Consulta de bitácora", "EXITOSO",
        f"El supervisor '{request.user.username}' accedió a los registros de auditoría."
    )

    return render(request, 'bienes/bitacora.html', {'eventos': eventos})