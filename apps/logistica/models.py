from django.db import models

class Direccion(models.Model):
    # Capa de Dominio: Atributos puros de la entidad
    calle_numero = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)

    class Meta:
        db_table = 'direcciones'


class Bien(models.Model):
    # Capa de Dominio: Entidad Bien vinculada a un usuario por su ID
    usuario_id = models.IntegerField()  # Almacena el ID del cliente manualmente
    descripcion = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    estatus = models.CharField(max_length=20, default='pendiente')
    
    # Llaves foráneas explícitas hacia direcciones
    direccion_recoleccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, related_name='recolecciones')
    direccion_entrega = models.ForeignKey(Direccion, on_delete=models.CASCADE, related_name='entregas')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bienes'