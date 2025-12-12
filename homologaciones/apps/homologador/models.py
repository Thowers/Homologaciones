from django.db import models

class Carrera(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.nombre

class AsignaturaDestino(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20)
    creditos = models.IntegerField()
    # Campo crucial para la IA: el contenido temático completo
    contenido_tematico = models.TextField(help_text="Descripción detallada del contenido que Gemini usará para la comparación.") 
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"