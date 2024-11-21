from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/', include('product.urls')),  
    path('category/<str:category>/', views.home, name='index_category'),
    path('new/', views.new_product, name='new'),
    path('new_category/', views.new_category, name='new_category'),
    path('user_admin_view/', views.user_admin_view, name='user_admin_view'),
    path('order_admin_view/', views.order_admin_view, name='order_admin_view'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('shopping_cart/', include('shoppingCart.urls')),  
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
