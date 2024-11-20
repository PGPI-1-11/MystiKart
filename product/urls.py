from django.urls import path
from .views import catalog_view, home_view

app_name = 'product'

urlpatterns = [
    path('', home_view, name='home'),  # URL de la página principal
    path('catalog/', catalog_view, name='catalog'),  # URL del catálogo
]
