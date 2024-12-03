from django.db import models
from product.models import Product
from custom_user.models import User

# Modelo de Elemento de Carrito (Items en el carrito)
class CartItem(models.Model):
    user = models.ForeignKey(User, related_name='cart_item', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    is_processed = models.BooleanField(default=False)

    class Meta:
        verbose_name = ("Artículo del carrito")
        verbose_name_plural = ("Artículos del carrito")

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

# Modelo de Dirección de Envío (Shipping Address)
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=1024)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)

    class Meta:
        verbose_name = ("Dirección de envío")
        verbose_name_plural = ("Direcciones de envío")



    def __str__(self):
        return f"{self.full_name}, {self.city}, {self.country}"


