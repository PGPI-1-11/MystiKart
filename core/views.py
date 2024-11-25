from django.shortcuts import render
from product.models import Category, Product, Brand
from shoppingCart.models import CartItem

def home(request):
    mensaje = ""
    mensaje_cantidad = ""
    
    # Cargar productos, categorías, marcas y carrito de compras
    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()
    cart = request.session.get('cart', {})
    cart_items = []
    precio_total = 0
    
    # Mensajes de sesión (si existen)
    if 'carrito_vacio' in request.session:
        mensaje = request.session.pop('carrito_vacio', None)
    
    if 'cantidad_superada' in request.session:
        mensaje_cantidad = request.session.pop('cantidad_superada', None)
    
    # Calcular el total del carrito
     # Calcular el total del carrito usando la función calcular_total
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            precio_total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            # Si el producto ya no existe, lo eliminamos del carrito
            del cart[product_id]
            request.session['cart'] = cart


    # Filtros para productos
    category = request.GET.get('category', None)
    brand = request.GET.get('brand', None)
    query = request.GET.get('q')

    # Aplicar filtros basados en los parámetros
    if category and brand and query:
        products = Product.objects.filter(brand__name=brand, category__name=category, name__icontains=query)
    elif category and brand:
        products = Product.objects.filter(category__name=category, brand__name=brand)
    elif category and query:
        products = Product.objects.filter(category__name=category, name__icontains=query)
    elif brand and query:
        products = Product.objects.filter(brand__name=brand, name__icontains=query)
    elif category:
        products = Product.objects.filter(category__name=category)
    elif brand:
        products = Product.objects.filter(brand__name=brand)
    elif query:
        products = Product.objects.filter(name__icontains=query)

    # Determinar si no hay productos para mostrar
    no_products = not products.exists()

    # Renderizar la plantilla home.html
    return render(request, 'home.html', {
        'categories': categories,
        'brands': brands,
        'products': products,
        'category_filter': category,
        'brand_filter': brand,
        'cart_items': cart_items,
        'precio_total': precio_total,
        'mensaje': mensaje,
        'mensaje_cantidad': mensaje_cantidad,
        'no_products': no_products,
    })

# Función para calcular el total del carrito
def calcular_total(items):
    precio_total = 0
    for item in items:
        precio_por_cantidad = item.quantity * item.product.price
        precio_total += precio_por_cantidad
    return precio_total
