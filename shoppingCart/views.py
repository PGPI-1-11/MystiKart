from django.shortcuts import get_object_or_404, render, redirect
from .models import CartItem, ShippingAddress
from product.models import Product
from django.contrib.auth.decorators import login_required
from .models import CartItem, ShippingAddress
from .forms import ShippingAddressForm 
from django.contrib import messages




def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart
    return redirect('cart_detail')




def cart_detail(request):
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            if request.user.is_authenticated:
                shipping_address.user = request.user  # Asocia la dirección al usuario autenticado
            shipping_address.save()
            messages.success(request, 'Dirección confirmada')  # Agrega el mensaje de confirmación
            return redirect('cart_detail')  # Redirige a la misma vista para mostrar el mensaje

    else:
        form = ShippingAddressForm()

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_processed=False)
    else:
        cart_items = []
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': product.price * quantity
            })

    total = sum(item['subtotal'] if isinstance(item, dict) else item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart_detail.html', {
        'cart_items': cart_items,
        'total': total,
        'form': form,
    })



def checkout_view(request):
    if request.user.is_authenticated:
        # Para usuarios autenticados
        cart_items = CartItem.objects.filter(user=request.user, is_processed=False)
    else:
        # Para usuarios no autenticados
        cart_items = []
        cart = request.session.get('cart', {})
        
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': product.price * quantity
            })

    total = sum(item['subtotal'] if isinstance(item, dict) else item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        # Simulación de procesamiento de pago y confirmación
        if request.user.is_authenticated:
            for item in cart_items:
                item.is_processed = True
                item.save()
        else:
            # Vaciar el carrito de la sesión después de procesar el pedido
            request.session['cart'] = {}

        return redirect('order_confirmation')

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total': total})

def order_confirmation(request):
    return render(request, 'confirmation.html')
