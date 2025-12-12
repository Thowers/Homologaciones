from django.contrib import admin
# La importación debe reflejar la ubicación de los modelos dentro de esta app.
from .models import Carrera, AsignaturaDestino 

# Registrar el modelo Carrera
admin.site.register(Carrera)

# Registrar el modelo AsignaturaDestino con ModelAdmin (opcional pero recomendado)
class AsignaturaDestinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'carrera', 'creditos') 
    search_fields = ('nombre', 'codigo', 'contenido_tematico')
    list_filter = ('carrera',) 

admin.site.register(AsignaturaDestino, AsignaturaDestinoAdmin)