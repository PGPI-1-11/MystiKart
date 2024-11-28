from django.shortcuts import get_object_or_404, render, redirect
from product.models import Product
from shoppingCart.models import CartItem
from .forms import ShippingAddressForm 
from django.contrib import messages
from django.http import JsonResponse
from django.middleware.csrf import get_token



from django.shortcuts import redirect

def add_to_cart(request, product_id):
    if request.method == 'POST':
        # Obtener el producto
        product = get_object_or_404(Product, id=product_id)

        # Obtener el carrito de la sesión
        cart = request.session.get('cart', {})

        # Obtener la cantidad solicitada
        quantity = int(request.POST.get('quantity', 1))

        # Comprobar el stock disponible
        if cart.get(str(product_id), 0) + quantity > product.stock:
            messages.error(request, 'No hay suficiente stock disponible.')
            return redirect('home')

        # Actualizar o agregar el producto al carrito
        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity

        # Guardar el carrito en la sesión
        request.session['cart'] = cart

        # Redirigir de vuelta al inicio o donde corresponda
        return redirect('home')  # Cambia 'home' por la página adecuada
    else:
        return redirect('home')



def cart_detail(request):
    form = ShippingAddressForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        shipping_address = form.save(commit=False)
        if request.user.is_authenticated:
            shipping_address.user = request.user
        shipping_address.save()
        messages.success(request, 'Dirección confirmada')
        return redirect('shoppingCart:cart_detail')

    cart_items = []
    precio_total = 0

    if request.user.is_authenticated:
        # Cargar los CartItem del usuario autenticado
        user_cart_items = CartItem.objects.filter(user=request.user, is_processed=False)
        for item in user_cart_items:
            subtotal = item.product.price * item.quantity
            precio_total += subtotal
            cart_items.append(item)
    else:
        # Cargar desde la sesión si el usuario no está autenticado
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            precio_total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })

    return render(request, 'cart_detail.html', {
        'cart_items': cart_items,
        'precio_total': precio_total,
        'form': form,
    })

def checkout_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    precio_total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        precio_total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    if request.method == 'POST':
        # Aquí podrías implementar la lógica del pago
        request.session['cart'] = {}  # Vaciar el carrito
        return redirect('shoppingCart:order_confirmation')

    return render(request, 'checkout.html', {'cart_items': cart_items, 'precio_total': precio_total})

def order_confirmation(request):
    return render(request, 'confirmation.html', {'is_confirmation_page': True})


def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})

        # Verificar si el producto está en el carrito
        if str(product_id) in cart:
            # Verificar si se quiere eliminar todo
            remove_all = request.POST.get('remove_all', False)  # Detecta si es "eliminar todo"
            
            if remove_all:
                del cart[str(product_id)]  # Elimina todo el producto del carrito
            else:
                cart[str(product_id)] -= 1  # Reduce 1 unidad
                if cart[str(product_id)] <= 0:
                    del cart[str(product_id)]  # Eliminar el producto si su cantidad es 0

            # Actualizar el carrito en la sesión
            request.session['cart'] = cart

        # Verificar el parámetro 'next' para redirigir a la página correspondiente
        next_url = request.POST.get('next', 'home')  # Redirige a 'home' por defecto
        return redirect(next_url)  # Redirige al home o al carrito según corresponda
    else:
        # Si no es un método POST, redirigir al home
        return redirect('home')
