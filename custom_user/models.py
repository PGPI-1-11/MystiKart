from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models

class User(BaseUser):
    first_name = models.CharField(max_length=30, blank=True, null=True, verbose_name="Nombre")
    last_name = models.CharField(max_length=30, blank=True, null=True, verbose_name="Apellidos")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    ciudad = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ciudad")
    codigo_postal = models.CharField(max_length=10, blank=True, null=True, verbose_name="Código Postal")
    pais = models.CharField(max_length=50, blank=True, null=True, verbose_name="País")

    objects = BaseUserManager()

    def __str__(self):
        return self.email
