from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class Usuario(AbstractUser):
    telefono = models.CharField(max_length=15, blank=True)


class Estado(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


class Tarea(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tareas')
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100)
    objetivos = models.TextField(blank=True)
    fecha_limite = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre