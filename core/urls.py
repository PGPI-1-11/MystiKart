from django.urls import include, path

from auth_user.views import RegistrationView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', include('auth_user.urls')),
    path('registro', RegistrationView.as_view(), name='registro'),

   
]