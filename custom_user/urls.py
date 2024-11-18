from django.urls import path
from .views import RegistrationView
from custom_user.views import RegistrationView, MyLoginView
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('users/', views.user_admin_view, name='user_admin_view'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('order/<int:order_id>/review/', views.order_review, name='order_review_admin')
]