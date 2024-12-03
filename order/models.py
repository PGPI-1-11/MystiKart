from django.db import models
from custom_user.models import User
from shoppingCart.models import CartItem

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

    # Detalles del pedido
    items = models.ManyToManyField(CartItem, related_name='order_items')
    user = models.ForeignKey(User, related_name='order_user', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, null=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PROCESADO)
    precio_total = models.FloatField()
    id_tracking = models.CharField(max_length=10, default=None)
    shipping_cost = models.FloatField(default=10.0)
    delivery_option = models.CharField(max_length=20, choices=DeliveryOptions.choices, default=DeliveryOptions.DOMICILIO)

    # Datos de pago
    payment_option = models.CharField(
        max_length=20,
        choices=PaymentOptions.choices,
        default=PaymentOptions.CONTRA_REEMBOLSO
    )
    cardholder_name = models.CharField(max_length=255, null=True, blank=True)
    card_number = models.CharField(max_length=16, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    cvv = models.CharField(max_length=3, null=True, blank=True)

    class Meta:
        verbose_name = ("Pedido")
        verbose_name_plural = ("Pedidos")


    @property
    def total_price_with_shipping(self):
        return self.precio_total if self.precio_total > 100.0 else self.precio_total + self.shipping_cost

    def __str__(self):
        return f"Order {self.id} - {self.status} - {self.user.email if self.user else 'Guest'}"
