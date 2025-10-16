from django.shortcuts import render, redirect
from .forms import MateriaForm
from .models import Materia
from django.contrib import messages

def crear_materia(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Materia registrada correctamente.')
            return redirect('materias:listar')
    else:
        form = MateriaForm()

    return render(request, 'materias/form_materia.html', {'form': form})


def listar_materias(request):
    materias = Materia.objects.all().order_by('-fecha_creacion')
    return render(request, 'materias/listar.html', {'materias': materias})