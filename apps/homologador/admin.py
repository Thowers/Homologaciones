from django.contrib import admin
from .models import Carrera, AsignaturaDestino, HistoricoHomologacion

admin.site.register(Carrera)

class AsignaturaDestinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'carrera', 'creditos') 
    search_fields = ('nombre', 'codigo', 'contenido_tematico')
    list_filter = ('carrera',) 

admin.site.register(AsignaturaDestino, AsignaturaDestinoAdmin)

class HistoricoHomologacionAdmin(admin.ModelAdmin):
    list_display = ('fecha_procesamiento', 'carrera_destino', 'nombre_estudiante', 'archivo_pdf_nombre')
    list_filter = ('carrera_destino', 'fecha_procesamiento')
    search_fields = ('nombre_estudiante', 'documento_identidad', 'archivo_pdf_nombre')
    readonly_fields = ('fecha_procesamiento', 'carrera_destino', 'archivo_pdf_nombre')
    ordering = ('-fecha_procesamiento',)
admin.site.register(HistoricoHomologacion, HistoricoHomologacionAdmin)