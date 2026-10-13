import calendar # El calendario de python ya que viene directamente con meses, semanas y días, siendo mucho mas sencillo
from datetime import date, timedelta # Importa date que es una fecha y timedelta que es una duración de tiempo, en este caso se usa para calcular el mes anterior y el siguiente
from django.contrib import messages # Mensajes de Django estilo: "Datos guardados correctamente."
from django.contrib.auth.decorators import login_required # Decorador q se asegurara de que solo los usuarios autenticados puedan acceder a ellas.
from django.db.models import F # Permite referenciar campos de modelos en consultas, útil para ordenar tareas por fecha límite, incluso si algunas son nulas.
from django.http import Http404 # Error de 'página no encontrada'
from django.shortcuts import get_object_or_404, render, redirect # get_object_or_404: obtiene un objeto o devuelve un error 404 si no se encuentra, render: renderiza una plantilla con un contexto, redirect: redirige a otra vista
from django.views.decorators.http import require_POST # Decorador que asegura que la vista solo acepte solicitudes POST, para acciones como cambiar el estado de una tarea o borrar una tarea.
from .forms import TareaForm, AjustesForm # Formularios personalizados para crear/editar tareas y ajustar la configuración del usuario
from .models import Estado, Tarea # Los modelos de las tablas de models.py
from django.contrib.auth import login # Función para iniciar sesión automáticamente después de registrar un nuevo usuario
from .forms import TareaForm, AjustesForm, RegistroForm # Igual que arriba, pero se agrega RegistroForm para el registro de nuevos usuarios

MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'] #Lista de los meses q sustituye el número por el nombre del mes.


def datos_calendario(anio, mes, usuario):
    
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
            'semanas': datos_calendario(hoy.year, hoy.month, request.user), #hoy.year y hoy.month nos muestra en el calendario el año y mes actual, RECORDAR QUE LAS LISTAS 
            'mes_nombre': MESES[hoy.month - 1], # SE DEBE DE MOSTRAR EL -1 YA QUE EMPIEZA EN ÍNDICE 0 
            'anio': hoy.year,
        }
    return render(request, 'tareas/principal.html', contexto)


@login_required
def lista_tareas(request):
    tareas = (Tarea.objects.filter(usuario=request.user)
              .select_related('estado')
              .order_by(F('fecha_limite').asc(nulls_last=True)))
    return render(request, 'tareas/lista_tareas.html', {
        'tareas': tareas,
        'estados': Estado.objects.all(),
    })


@login_required
def crear_tarea(request):
    if request.method == 'POST': # POST lo que hace es recibir, validar y guardar la tarea
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
        raise Http404  #Este bloque de código lo que muestra es que si el mes no está entre 1 y 12, ej: /calendario/2026/13/ , se genera un error 404, ya que no existe ese mes.

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


@login_required
@require_POST
def cambiar_estado(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, usuario=request.user)
    estado_id = request.POST.get('estado', '')
    if estado_id.isdigit():
        tarea.estado = get_object_or_404(Estado, pk=int(estado_id))
        tarea.save(update_fields=['estado'])
    return redirect('tareas_activas')


@login_required
def editar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            return redirect('tareas_activas')
    else:
        form = TareaForm(instance=tarea)
    return render(request, 'tareas/editar_tarea.html', {'form': form, 'tarea': tarea})


@login_required
def borrar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, usuario=request.user)
    if request.method == 'POST':
        tarea.delete()
        return redirect('tareas_activas')
    return render(request, 'tareas/borrar_tarea.html', {'tarea': tarea})

def registro(request):
    if request.user.is_authenticated:
        return redirect('principal')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('principal')
    else:
        form = RegistroForm()
    return render(request, 'tareas/registro.html', {'form': form})


@login_required
@require_POST
def borrar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, usuario=request.user)
    tarea.delete()
    return redirect('tareas_activas')