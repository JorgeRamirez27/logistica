from django import forms
from .models import Direccion

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = [
            'identificador', 'calle', 'numero', 'colonia', 
            'ciudad', 'estado', 'codigo_postal', 
        ]
        
    def __init__(self, *args, **kwargs):
        super(DireccionForm, self).__init__(*args, **kwargs)
        # Le damos estilo Bootstrap a todos los campos rápidamente
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    