import calendar
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from .forms import TareaForm, AjustesForm
from .models import Tarea

MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def datos_calendario(anio, mes, usuario):
    """Semanas del mes; cada día lleva las tareas activas del usuario con fecha límite ese día."""
    tareas = Tarea.objects.filter(
        usuario=usuario,
        estado__nombre='Activo',
        fecha_limite__year=anio,
        fecha_limite__month=mes,
    )
    por_dia = {}
    for t in tareas:
        por_dia.setdefault(t.fecha_limite.day, []).append(t)

    semanas = []
    for semana in calendar.Calendar(firstweekday=0).monthdayscalendar(anio, mes):
        semanas.append([{'dia': d, 'tareas': por_dia.get(d, [])} for d in semana])
    return semanas


def principal(request):
    contexto = {}
    if request.user.is_authenticated:
        hoy = date.today()
        contexto = {
            'proximas': (Tarea.objects
                         .filter(usuario=request.user, estado__nombre='Activo',
                                 fecha_limite__isnull=False)
                         .order_by('fecha_limite')[:3]),
            'semanas': datos_calendario(hoy.year, hoy.month, request.user),
            'mes_nombre': MESES[hoy.month - 1],
            'anio': hoy.year,
        }
    return render(request, 'tareas/principal.html', contexto)


@login_required
def lista_tareas(request):
    tareas = (Tarea.objects.filter(usuario=request.user)
              .select_related('estado').order_by('fecha_limite'))
    return render(request, 'tareas/lista_tareas.html', {'tareas': tareas})


@login_required
def crear_tarea(request):
    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.usuario = request.user
            tarea.save()
            return redirect('tareas_activas')
    else:
        form = TareaForm()
    return render(request, 'tareas/crear_tarea.html', {'form': form})


@login_required
def calendario(request, anio=None, mes=None):
    hoy = date.today()
    anio = anio or hoy.year
    mes = mes or hoy.month
    if not 1 <= mes <= 12:
        raise Http404

    anterior = date(anio, mes, 1) - timedelta(days=1)
    siguiente = date(anio, mes, 28) + timedelta(days=4)

    return render(request, 'tareas/calendario.html', {
        'semanas': datos_calendario(anio, mes, request.user),
        'mes_nombre': MESES[mes - 1],
        'anio': anio,
        'anterior': anterior,
        'siguiente': siguiente,
    })


@login_required
def ajustes(request):
    if request.method == 'POST':
        form = AjustesForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos guardados correctamente.')
            return redirect('ajustes')
    else:
        form = AjustesForm(instance=request.user)
    return render(request, 'tareas/ajustes.html', {'form': form})