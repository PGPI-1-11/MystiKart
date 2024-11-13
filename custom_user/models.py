from django_use_email_as_username.models import BaseUser, BaseUserManager


class User(BaseUser):
    objects = BaseUserManager()

    class Meta:
        app_label = 'custom_user'