from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required  
from django.core.exceptions import PermissionDenied
from django.db.models import RestrictedError
from django.contrib import messages

from apps.bienes.views import registrar_en_bitacora 
from .models import Cliente, Direccion
from .forms import DireccionForm

@login_required
def registrar_direccion(request):
    """
    Entry Point: Permite al cliente agregar una dirección a su agenda privada.
    """
    if not request.user.groups.filter(name='Cliente').exists() and not request.user.is_superuser:
        registrar_en_bitacora(request, "Alta de dirección", "RECHAZADO", "Acceso denegado por rol.")
        raise PermissionDenied("No tienes permisos para agregar direcciones.")

    try:
        cliente_perfil = Cliente.objects.get(correo=request.user.email)
    except Cliente.DoesNotExist:
        raise PermissionDenied("Tu cuenta no está vinculada a un perfil logístico.")

    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.cliente = cliente_perfil
            direccion.tipo = ''
            direccion.save()
            
            registrar_en_bitacora(
                request, "Alta de dirección", "EXITOSO", 
                f"Dirección '{direccion.identificador}' guardada en la agenda del cliente."
            )
            return redirect('bienes:lista_bienes')
    else:
        form = DireccionForm()

    return render(request, 'clientes/registrar_direccion.html', {'form': form})

@login_required
def listar_direcciones(request):
    cliente_perfil = Cliente.objects.get(correo=request.user.email)
    direcciones = Direccion.objects.filter(cliente=cliente_perfil)
    
    return render(request, 'clientes/lista_direcciones.html', {
        'direcciones': direcciones
    })

@login_required
def editar_direccion(request, pk):
    cliente_perfil = Cliente.objects.get(correo=request.user.email)
    direccion = get_object_or_404(Direccion, pk=pk, cliente=cliente_perfil)
    
    if request.method == 'POST':
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, "Dirección actualizada correctamente.")
            return redirect('clientes:listar_direcciones')
    else:
        form = DireccionForm(instance=direccion)
        
    return render(request, 'clientes/registrar_direccion.html', {'form': form})

@login_required
def eliminar_direccion(request, pk):
    cliente_perfil = Cliente.objects.get(correo=request.user.email)
    direccion = get_object_or_404(Direccion, pk=pk, cliente=cliente_perfil)
    
    if request.method == 'POST':
        try:
            # Intentamos borrar la dirección
            direccion.delete()
            messages.success(request, "La dirección fue eliminada de tu agenda.")
        except RestrictedError:
            # Si Django detecta que está en uso, bloquea el borrado y lanza este mensaje
            messages.error(
                request, 
                "No puedes eliminar esta dirección porque actualmente es el Origen o Destino de un paquete registrado."
            )
        return redirect('clientes:listar_direcciones')
        
    return render(request, 'clientes/confirmar_eliminar.html', {'direccion': direccion})