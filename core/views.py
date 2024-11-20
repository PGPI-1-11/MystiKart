from django.shortcuts import render

from product.models import Category, Product
from shoppingCart.models import CartItem

def home(request):
    mensaje = ""
    mensaje_cantidad = ""
    products = Product.objects.all()
    categories = Category.objects.all()
    shoppingCarts = CartItem.objects.filter(user_id=request.user.id, is_processed=False)
    
    if 'carrito_vacio' in request.session:
        mensaje = request.session.pop('carrito_vacio', None)

    if 'cantidad_superada' in request.session:
        mensaje_cantidad = request.session.pop('cantidad_superada', None)
    
    total = calcular_total(shoppingCarts)

    category = request.GET.get('category', None)
    query = request.GET.get('q')

    if category and query:
        products = Product.objects.filter(category__name=category, name__icontains=query)
    elif category:
        products = Product.objects.filter(category__name=category)
    elif query:
        products = Product.objects.filter(name__icontains=query)

    no_products = not products.exists()
    
    return render(request, 'home.html', {
        'categories': categories,
        'products': products,
        'category_filter': category,
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
