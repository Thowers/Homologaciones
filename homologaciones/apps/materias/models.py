from django.db import models

class Materia(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    embedding_generado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre