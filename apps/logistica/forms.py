from django import forms
from django.core.exceptions import ValidationError

class FormularioAltaBien(forms.Form):
    # Campos del formulario de presentación
    descripcion = forms.CharField(max_length=255, required=True)
    valor = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    
    # Campos para la dirección de recolección
    rec_calle = forms.CharField(max_length=255, required=True)
    rec_ciudad = forms.CharField(max_length=100, required=True)
    rec_estado = forms.CharField(max_length=100, required=True)
    rec_cp = forms.CharField(max_length=10, required=True)
    
    # Campos para la dirección de entrega
    ent_calle = forms.CharField(max_length=255, required=True)
    ent_ciudad = forms.CharField(max_length=100, required=True)
    ent_estado = forms.CharField(max_length=100, required=True)
    ent_cp = forms.CharField(max_length=10, required=True)

    # Validaciones específicas al estilo de la clase
    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor <= 0:
            raise ValidationError("El valor del bien debe ser un número positivo mayor que cero.")
        return valor

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        # Sanitización simple: evitar caracteres sospechosos de scripts (< >)
        if "<" in descripcion or ">" in descripcion:
            raise ValidationError("La descripción contiene caracteres no permitidos.")
        return descripcion