from django.urls import path

from .views import  checkout_view, home_view, product_info, search_product



app_name = 'product'

urlpatterns = [
    path('', home_view, name='home'),  # URL de la página principal
    path('<int:pk>/', product_info, name='product_info'),  # URL de la información del producto
    path('search/', search_product, name='search_product'),
]