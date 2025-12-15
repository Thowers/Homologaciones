from django.urls import path
from . import views

urlpatterns = [
    # ➡️ ENLAZA LA RUTA VACÍA (la que recibe del principal) A LA VISTA
    path('', views.procesar_homologacion_view, name='procesar_homologacion'),
    path('descargar/<int:historico_id>/', views.descargar_docx_homologacion, name='descargar_docx'),
]