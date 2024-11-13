from django.db import models
from custom_user.models import User
from django.core.validators import MinValueValidator

# Modelo de Categoría para productos (con subcategorías opcionales)
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        ordering = ('name',)
        verbose_name_plural='Categories'

    def __str__(self):
        return self.name

# Modelo de Producto
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price=models.FloatField(validators=[MinValueValidator(0.0, message="El precio no puede ser negativo")])
    stock = models.IntegerField(default=0,validators=[MinValueValidator(0, message="El stock no puede ser negativo")])
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images', blank=True, null=True)

    def is_in_stock(self):
        return self.stock > 0


    def __str__(self):
        return self.name
