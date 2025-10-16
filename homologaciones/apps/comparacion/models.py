from django.db import models
from apps.materias.models import Materia

class Homologacion(models.Model):
    materia_origen = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='comparacion_origen')
    materia_destino = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='comparacion_destino')
    similitud = models.FloatField()
    creada_en = models.DateTimeField(auto_now_add=True)