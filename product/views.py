from django.shortcuts import render

from core.views import calcular_total
from shoppingCart.models import CartItem
from .models import Category, Product

# Vista para la página principal, con las categorías y productos relacionados
def home_view(request):
    categories = Category.objects.prefetch_related('product_set').all()
    return render(request, 'catalog.html', {'categories': categories})

# Vista para el catálogo de productos, también obtiene las categorías y productos
def catalog_view(request):
    categories = Category.objects.prefetch_related('product_set').all()
    return render(request, 'catalog.html', {'categories': categories})

def product_info(request, pk):
    try:
        mensaje=""
        mensaje_cantidad=""
        product = Product.objects.get(pk=pk)
        shoppingCarts = CartItem.objects.filter(user_id=request.user.id, is_processed=False)
        if 'carrito_vacio' in request.session:
            mensaje=request.session.pop('carrito_vacio',None)

        if 'cantidad_superada' in request.session:
            mensaje_cantidad=request.session.pop('cantidad_superada',None)
        total = calcular_total(shoppingCarts)

        
    except Product.DoesNotExist:
        return render(request, 'product/404.html', {})

    return render(request, 'product/info.html', {
        'product': product,
        'cart_items':shoppingCarts,
        'precio_total':total,
        'mensaje':mensaje,
        'mensaje_cantidad':mensaje_cantidad,})