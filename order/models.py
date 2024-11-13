from django.db import models
from custom_user.models import User
from shoppingCart.models import CartItem


class Review(models.Model):
    class AcceptionStatus(models.TextChoices):
        ACCEPTED = 'aceptado', 'Aceptado'
        PENDING = 'pendiente', 'Pendiente'
        DECLINED = 'rechazado', 'Rechazado'

    title = models.CharField(max_length=50, blank=False, null=False)
    description = models.CharField(max_length=255, blank=False, null=False)
    is_accepted = models.CharField(max_length=20, choices=AcceptionStatus.choices, default=AcceptionStatus.PENDING)

    def _str_(self):
        return self.title

# Modelo de Pedido (Order)
class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PROCESADO = 'procesado', 'Procesado'
        ENVIADO = 'enviado', 'Enviado'
        COMPLETADO = 'completado', 'Completado'

    class DeliveryOptions(models.TextChoices):
        DOMICILIO = 'Domicilio', 'Domicilio'
        CORREOS = 'Correos', 'Correos'

    class PaymentOptions(models.TextChoices):
        CONTRA_REEMBOLSO = 'contra_reembolso', 'Contra reembolso'
        TARJETA = 'tarjeta', 'Tarjeta'


    #products = models.ManyToManyField(Product, related_name='order_products')
    items = models.ManyToManyField(CartItem, related_name='order_items')
    user = models.ForeignKey(User, related_name='order_user', on_delete=models.CASCADE, null=True)
    review = models.OneToOneField(Review, related_name='order_review', on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(max_length=100, null=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=None, null=True)
    precio_total = models.FloatField()
    id_tracking = models.CharField(max_length=10, default=None)
    shipping_cost = models.FloatField(default=10.0)
    precio_total = models.FloatField()
    delivery_option = models.CharField(max_length=20, choices=DeliveryOptions.choices, default=DeliveryOptions.DOMICILIO)
    payment_option = models.CharField(max_length=20, choices=PaymentOptions.choices, default=PaymentOptions.CONTRA_REEMBOLSO)

    @property
    def total_price_with_shipping(self):
        if self.precio_total > 100.0:
            return self.precio_total
        else:
            return self.precio_total + self.shipping_cost