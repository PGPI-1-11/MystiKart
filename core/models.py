from django.contrib.auth.models import User
from django.db import models

# Perfil de usuario extendido para datos adicionales
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_registered = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Modelo de Categoría para productos (con subcategorías opcionales)
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)  # Para categorías anidadas
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

# Modelo de Producto
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()  # Unidades en stock
    is_available = models.BooleanField(default=True)  # Si está disponible
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # Categoría del producto
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    manufacturer = models.CharField(max_length=255, blank=True, null=True)  # Opcional
    slug = models.SlugField(unique=True)  # Para SEO y URL amigables

    def __str__(self):
        return self.name

# Modelo de Carrito de Compra (Carrito)
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Puede ser null si no está registrado
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user if self.user else 'Guest'}"

# Modelo de Elemento de Carrito (Items en el carrito)
class CartItem(models.Model):
    user = models.ForeignKey(User, related_name='cart_item', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    is_processed = models.BooleanField(default=False)

# Modelo de Dirección de Envío (Shipping Address)
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=1024)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.full_name}, {self.city}, {self.country}"



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

# Modelo de Pago (Payment)
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)  # Ejemplo: Tarjeta, PayPal, etc.
    payment_status = models.CharField(max_length=50)  # Ejemplo: Pagado, Fallido
    transaction_id = models.CharField(max_length=255)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"


# Modelo de Seguimiento de Pedido (Order Tracking)
class OrderTracking(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tracking {self.id} for Order {self.order.id}"


