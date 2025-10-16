from django.urls import path
from . import views

app_name = 'materias'

urlpatterns = [
    path('nueva/', views.crear_materia, name='nueva'),
    path('listar/', views.listar_materias, name='listar'),
]