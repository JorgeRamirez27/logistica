from django import forms
from django.utils.html import escape
from .models import Bien

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