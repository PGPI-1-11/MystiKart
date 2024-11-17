from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Hacemos el email único

    objects = BaseUserManager()

    class Meta:
        pass  # No necesitas app_label si ya está en INSTALLED_APPS
