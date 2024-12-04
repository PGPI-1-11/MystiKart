from django.urls import path
from . import views

app_name = 'shoppingCart'

urlpatterns = [
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
]