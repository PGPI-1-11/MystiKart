from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser

from django.db import models

class User(AbstractUser):
    username = models.CharField(null=True)
    email = models.EmailField(unique=True)