from django.urls import path
from .views import checkout_view, home_view, product_info

app_name = 'product'

urlpatterns = [
    path('', home_view, name='home'),
    path('<int:pk>/', product_info, name='product_info'),
]