from django.shortcuts import render, get_object_or_404

from core.views import calcular_total
from product.models import Product, Category
from shoppingCart.models import CartItem


def home_view(request):
    categories = Category.objects.prefetch_related('product_set').all()
    products = Product.objects.all()
    return render(request, 'home.html', {'categories': categories, 'products': products})

def checkout_view(request):
    cart_items = CartItem.objects.filter(user_id=request.user.id, is_processed=False)
    precio_total = 0
    for item in cart_items:
        precio_total += item.product.price * item.quantity  

    return render(request, 'checkout.html', {'cart_items': cart_items, 'precio_total': precio_total})

def product_info(request, pk):
    mensaje = ""
    mensaje_cantidad = ""
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})
    cart_items = []
    precio_total = 0

    if 'carrito_vacio' in request.session:
        mensaje = request.session.pop('carrito_vacio', None)

    if 'cantidad_superada' in request.session:
        mensaje_cantidad = request.session.pop('cantidad_superada', None)
    

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        precio_total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })
   

    return render(request, 'info.html', {
        'product': product,
        'cart_items': cart_items,
        'precio_total': precio_total,
        'mensaje': mensaje,
        'mensaje_cantidad': mensaje_cantidad,
    })
def search_product(request) :
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('category', None)

    productos = Product.objects.all() #Iniciamos todos los productos

    if query :
        productos = productos.filter(name__icontains=query)
    
    if categoria_id :
        productos = productos.filter(category_id=categoria_id)

    categorias = Category.objects.all()

    context = {
        'products' : productos, 
        'query' : query,
        'categoria_id' : categoria_id,
        'categories' : categorias,
    }

    return render(request, 'search_result.html', context)