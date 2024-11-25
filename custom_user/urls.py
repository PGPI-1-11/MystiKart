from django.urls import path
from .views import RegistrationView
from custom_user.views import RegistrationView, MyLoginView, StoreInfoView
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('users/', views.user_admin_view, name='user_admin_view'),
    path('registro/', RegistrationView.as_view(), name='registro'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('store_info/', StoreInfoView.as_view(), name='store_info'),
]