from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.order_search, name='order_search'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
]
