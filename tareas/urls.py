from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.principal, name='principal'),
    path('login/', auth_views.LoginView.as_view(template_name='tareas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('ajustes/', views.ajustes, name='ajustes'),
    path('tareas/', views.lista_tareas, name='tareas_activas'),
    path('tareas/nueva/', views.crear_tarea, name='crear_tarea'),
    path('calendario/', views.calendario, name='calendario'),
    path('calendario/<int:anio>/<int:mes>/', views.calendario, name='calendario_mes'),
]