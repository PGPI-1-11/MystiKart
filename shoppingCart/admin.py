from django.contrib import admin

from .models import CartItem, ShippingAddress

admin.site.register(CartItem)
admin.site.register(ShippingAddress)