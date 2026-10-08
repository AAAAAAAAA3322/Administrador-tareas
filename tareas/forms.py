from django import forms
from .models import Tarea, Usuario


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['estado', 'nombre', 'objetivos', 'fecha_limite']
        widgets = {
            'objetivos': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Un objetivo por línea'}),
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
        }


class AjustesForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
        }