from django.shortcuts import render, get_object_or_404

from core.views import calcular_total
from product.models import Product, Category
from shoppingCart.models import CartItem

def home_view(request):
    categories = Category.objects.prefetch_related('product_set').all()
    return render(request, 'catalog.html', {'categories': categories})

def catalog_view(request):
    categories = Category.objects.prefetch_related('product_set').all()
    return render(request, 'catalog.html', {'categories': categories})

def product_info(request, pk):
    mensaje = ""
    mensaje_cantidad = ""
    product = get_object_or_404(Product, pk=pk)
    shoppingCarts = CartItem.objects.filter(user_id=request.user.id, is_processed=False)
    
    if 'carrito_vacio' in request.session:
        mensaje = request.session.pop('carrito_vacio', None)

    if 'cantidad_superada' in request.session:
        mensaje_cantidad = request.session.pop('cantidad_superada', None)
    
    total = calcular_total(shoppingCarts)

    return render(request, 'product/info.html', {
        'product': product,
        'cart_items': shoppingCarts,
        'precio_total': total,
        'mensaje': mensaje,
        'mensaje_cantidad': mensaje_cantidad,
    })