from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Cliente

@receiver(post_save, sender=Cliente)
def automatizar_usuario_cliente(sender, instance, created, **kwargs):
    """
    Cuando se crea un Cliente nuevo, este Signal genera su Usuario de Django automáticamente
    para que pueda iniciar sesión sin tener que crearlo manualmente en Auth > Users.
    """
    if created:
        # 1. Creamos el usuario en la base de datos de Auth
        # Usamos el identificador como contraseña inicial
        user = User.objects.create_user(
            username=instance.identificador, 
            email=instance.correo,
            password=instance.identificador 
        )
        
        # 2. Lo metemos al grupo 'Cliente' automáticamente (si el grupo no existe, lo crea)
        grupo_cliente, _ = Group.objects.get_or_create(name='Cliente')
        user.groups.add(grupo_cliente)
        
    else:
        # Si el administrador actualiza el Cliente en el futuro, sincronizamos.
        try:
            user = User.objects.get(username=instance.identificador)
            if user.email != instance.correo:
                user.email = instance.correo
                user.save()
        except User.DoesNotExist:
            # Si el cliente fue creado ANTES de tener los signals, no tiene usuario. 
            # Se lo creamos en este momento para arreglar el problema retroactivamente.
            user = User.objects.create_user(
                username=instance.identificador, 
                email=instance.correo,
                password=instance.identificador 
            )
            grupo_cliente, _ = Group.objects.get_or_create(name='Cliente')
            user.groups.add(grupo_cliente)