from django.shortcuts import render
from product.models import Category, Product
from shoppingCart.models import CartItem

def home(request):
    mensaje = ""
    mensaje_cantidad = ""
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    # Mensajes para el usuario (si existen)
    if 'carrito_vacio' in request.session:
        mensaje = request.session.pop('carrito_vacio', None)

    if 'cantidad_superada' in request.session:
        mensaje_cantidad = request.session.pop('cantidad_superada', None)
    
    # Calcular el total del carrito usando la función calcular_total
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            # Si el producto ya no existe, lo eliminamos del carrito
            del cart[product_id]
            request.session['cart'] = cart

    # Filtrar productos por categoría si corresponde
    category_filter = request.GET.get('category', None)
    if category_filter:
        products = Product.objects.filter(category__name=category_filter)
    else:
        products = Product.objects.all()

    no_products = not products.exists()
    
    # Renderizar la vista con el contexto
    return render(request, 'home.html', {
        'categories': categories,
        'products': products,
        'category_filter': category_filter,
        'cart_items': cart_items,
        'precio_total': total,  # Asegurémonos de pasar 'total' como 'precio_total'
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
