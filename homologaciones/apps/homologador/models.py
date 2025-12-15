from django.db import models
from django.utils import timezone
import json

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
    
class HistoricoHomologacion(models.Model):
    carrera_destino = models.ForeignKey('Carrera', on_delete=models.SET_NULL, null=True, blank=True)    
    nombre_estudiante = models.CharField(max_length=200, blank=True, null=True, 
                                         help_text="Nombre del estudiante (si se puede extraer).")
    documento_identidad = models.CharField(max_length=50, blank=True, null=True, 
                                           help_text="Cédula o ID del estudiante.")
    resultado_json = models.TextField(help_text="Resultado completo de la homologación en formato JSON.")    
    fecha_procesamiento = models.DateTimeField(default=timezone.now)
    archivo_pdf_nombre = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Histórico de Homologación"
        verbose_name_plural = "Históricos de Homologación"
        ordering = ['-fecha_procesamiento']

    def __str__(self):
        return f"Homologación de {self.nombre_estudiante or 'Desconocido'} a {self.carrera_destino} - {self.fecha_procesamiento.strftime('%Y-%m-%d')}"
    
    @property
    def resultado_parsed(self):
        try:
            return json.loads(self.resultado_json)
        except:
            return None