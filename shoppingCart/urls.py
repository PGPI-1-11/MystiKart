from django.urls import path
from . import views

urlpatterns = [
    # Otras rutas
    path('carrito/', views.carrito, name='carrito'),
]
