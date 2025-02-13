from django.urls import path
from django.contrib import admin

from auth_user.views import RegistrationView, LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registro/', RegistrationView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
]