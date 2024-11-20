from django.shortcuts import render

from product.models import Category, Product
from shoppingCart.models import CartItem

def home(request):
    mensaje = ""
    mensaje_cantidad = ""
    categories = Category.objects.all()
    shoppingCarts = CartItem.objects.filter(user_id=request.user.id, is_processed=False)
    
    if 'carrito_vacio' in request.session:
        mensaje = request.session.pop('carrito_vacio', None)

    if 'cantidad_superada' in request.session:
        mensaje_cantidad = request.session.pop('cantidad_superada', None)
    
    total = calcular_total(shoppingCarts)

    category_filter = request.GET.get('category', None)
    if category_filter:
        products = Product.objects.filter(category__name=category_filter)
    else:
        products = Product.objects.all()

    no_products = not products.exists()
    
    return render(request, 'home.html', {
        'categories': categories,
        'products': products,
        'category_filter': category_filter,
        'cart_items': shoppingCarts,
        'precio_total': total,
        'mensaje': mensaje,
        'mensaje_cantidad': mensaje_cantidad,
        'no_products': no_products
    })

def calcular_total(items):
    precio_total = 0
    for item in items:
        precio_por_cantidad = item.quantity * item.product.price
        precio_total += precio_por_cantidad
    return precio_total
