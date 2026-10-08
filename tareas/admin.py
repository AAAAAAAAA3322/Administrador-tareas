from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Estado, Tarea  
# Register your models here.
admin.site.register(Usuario, UserAdmin)
admin.site.register(Estado)
admin.site.register(Tarea)