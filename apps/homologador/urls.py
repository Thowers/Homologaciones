from django.urls import path
from . import views

urlpatterns = [
    path('', views.procesar_homologacion_view, name='procesar_homologacion'),
    path('descargar/<int:historico_id>/', views.descargar_docx_homologacion, name='descargar_docx'),
]