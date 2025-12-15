from django import forms
from .models import Carrera

class NotasUploadForm(forms.Form):
    notas_file = forms.FileField(label='Subir Historial Académico (PDF)')
    carrera_destino = forms.ModelChoiceField(queryset=Carrera.objects.all(), label='Carrera de Destino')