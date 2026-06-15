from django import forms
from django.utils.html import escape
from .models import Bien
from apps.clientes.models import Direccion  # Asegúrate de importar el modelo Direccion

class BienForm(forms.ModelForm):
    class Meta:
        model = Bien
        fields = [
            'identificador', 
            'descripcion', 
            'marca', 
            'valor', 
            'direccion_recoleccion', 
            'direccion_entrega'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe el bien detalladamente...'}),
        }

    # ==========================================
    # AISLAMIENTO DE DATOS (AGENDA PRIVADA)
    # ==========================================
    def __init__(self, *args, **kwargs):
        # 1. Extraemos el cliente antes de inicializar el formulario base
        cliente_perfil = kwargs.pop('cliente', None)
        super(BienForm, self).__init__(*args, **kwargs)
        
        # 2. Filtro hermético: Solo mostramos las direcciones del cliente logueado
        if cliente_perfil:
            self.fields['direccion_recoleccion'].queryset = Direccion.objects.filter(
                cliente=cliente_perfil
            )
            self.fields['direccion_entrega'].queryset = Direccion.objects.filter(
                cliente=cliente_perfil
            )
            
            # Mejoramos la experiencia de usuario con placeholders claros
            self.fields['direccion_recoleccion'].empty_label = "Seleccione un origen de su agenda..."
            self.fields['direccion_entrega'].empty_label = "Seleccione un destino de su agenda..."

    # ==========================================
    # SANITIZACIÓN Y VALIDACIÓN (OWASP)
    # ==========================================

    def clean_identificador(self):
        """Normaliza el identificador a mayúsculas y limpia espacios."""
        identificador = self.cleaned_data.get('identificador', '')
        return identificador.strip().upper()

    def clean_descripcion(self):
        """
        Sanitización: Elimina espacios innecesarios al inicio y final.
        Escapa caracteres especiales para evitar ataques XSS almacenados.
        """
        descripcion = self.cleaned_data.get('descripcion', '')
        descripcion_limpia = descripcion.strip()
        # El método escape convierte <, >, ', " y & a entidades HTML seguras
        return escape(descripcion_limpia)

    def clean_marca(self):
        """Sanitización y normalización de la marca."""
        marca = self.cleaned_data.get('marca', '')
        return escape(marca.strip().upper())

    def clean_valor(self):
        """Validación de reglas de negocio para asegurar un valor correcto."""
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor <= 0:
            raise forms.ValidationError("El valor monetario debe ser estrictamente mayor a 0.")
        return valor