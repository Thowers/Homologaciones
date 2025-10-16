from django.db import models
from apps.materias.models import Materia

class Homologacion(models.Model):
    materia_origen = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='descripcion_origen')
    materia_destino = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='descripcion_destino')
    creada_en = models.DateTimeField(auto_now_add=True)