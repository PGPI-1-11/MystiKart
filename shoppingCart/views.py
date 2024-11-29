import secrets
import logging
from django.shortcuts import get_object_or_404, render, redirect
from MystiKart import settings
from order.models import Order
from product.models import Product
from shoppingCart.models import CartItem
from .forms import ShippingAddressForm 
from django.contrib import messages
import stripe
from django.shortcuts import redirect

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


def add_to_cart(request, product_id):
    if request.method == 'POST':
        # Obtener el producto
        product = get_object_or_404(Product, id=product_id)
        # Obtener la cantidad solicitada
        quantity = int(request.POST.get('quantity', 1))
        precio_total = 0

        # Comprobar si el usuario está autenticado
        if request.user.is_authenticated:
            # Usuario autenticado: manejar en base de datos
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user, 
                product=product, 
                is_processed=False, 
                defaults={'quantity': 0}
            )

            # Verificar stock disponible
            if cart_item.quantity + quantity > product.stock:
                messages.error(request, 'No hay suficiente stock disponible.')
                return redirect('home')

            # Actualizar la cantidad del producto
            cart_item.quantity += quantity
            cart_item.save()
            product.stock -= quantity
            product.save()         
        else:
            # Usuario no autenticado: manejar en la sesión
            cart = request.session.get('cart', {})

            # Verificar stock disponible
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
            product.stock -= quantity
            product.save()   
            
           

        # Redirigir de vuelta al inicio o donde corresponda
        messages.success(request, f'{product.name} se ha agregado al carrito.')
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
    precio_total_con_envio = 0

    # Calcular el costo de envío (ejemplo: 5€ si el total es menor a 100€, envío gratuito si es mayor)
    costo_envio = 10  # Valor fijo de ejemplo


    if request.user.is_authenticated:
        # Cargar los CartItem del usuario autenticado
        user_cart_items = CartItem.objects.filter(user=request.user, is_processed=False)
        for item in user_cart_items:
            subtotal = item.product.price * item.quantity
            precio_total += subtotal
            cart_items.append(item)
    else:
        
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

    # Lógica para aplicar el costo de envío
    if precio_total < 100:  # Si el total es menor a 100€, agregar coste de envío
        precio_total_con_envio = precio_total + costo_envio
    else:
        precio_total_con_envio = precio_total # Envío gratuito

    return render(request, 'cart_detail.html', {
        'cart_items': cart_items,
        'precio_total': precio_total,
        'precio_total_con_envio': precio_total_con_envio,
        'form': form,
        'costo_envio': costo_envio if precio_total < 100 else 0,  # Mostrar el costo si es aplicable
    })

def generate_unique_random_string(length=10):
    while True: 
        random_string = secrets.token_urlsafe(length)[:length]
        if not Order.objects.filter(id_tracking=random_string).exists():
            break
    return random_string


def checkout_view(request):
    cart_items = []
    precio_total = 0

    if request.user.is_authenticated:
        # Obtener items del carrito para usuarios autenticados
        cart_items = CartItem.objects.filter(user=request.user, is_processed=False).select_related('product')
        for item in cart_items:
            subtotal = item.product.price * item.quantity
            precio_total += subtotal
    else:
        # Obtener items del carrito de la sesión
        cart = request.session.get('cart', {})
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
                continue

    if not cart_items:
        messages.error(request, "El carrito no puede estar vacío")
        return redirect('shoppingCart:cart_detail')

    # Calcular costos de envío
    shipping_cost = 0.0 if precio_total > 100.0 else 10.0
    precio_total_con_envio = precio_total + shipping_cost

    if request.method == 'POST':
        payment_option = request.POST.get('payment_option')
        delivery_option = request.POST.get('delivery_option')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')

        if not address or not city or not zip_code or not country:
            messages.error(request, 'Todos los campos de dirección son obligatorios')
            return redirect('shoppingCart:checkout_view')

        email = request.user.email if request.user.is_authenticated else request.POST.get('email')
        if not email:
            messages.error(request, 'El correo electrónico es obligatorio')
            return redirect('shoppingCart:checkout_view')

        # Generar tracking ID
        tracking = generate_unique_random_string()

        try:
            # Procesar pago con tarjeta
            if payment_option == 'tarjeta':
                token = request.POST.get('stripeToken')
                if not token:
                    messages.error(request, 'Debe proporcionar los datos de la tarjeta para procesar el pago.')
                    return redirect('shoppingCart:checkout_view')


                try:
                    charge = stripe.Charge.create(
                        amount=int(precio_total_con_envio * 100),
                        currency='eur',
                        description='Compra en MystiKart',
                        source=token,
                    )
                except stripe.error.CardError as e:
                    messages.error(request, f'Error en la tarjeta: {e.error.message}')
                    return redirect('shoppingCart:checkout_view')

            # Crear el pedido
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                address=address,
                city=city,
                zip_code=zip_code,
                country=country,
                email=email,
                status=Order.StatusChoices.PROCESADO,
                precio_total=precio_total,
                shipping_cost=shipping_cost,
                id_tracking=tracking,
                delivery_option=delivery_option,
                payment_option=Order.PaymentOptions.TARJETA if payment_option == 'tarjeta' else Order.PaymentOptions.CONTRA_REEMBOLSO
            )

            # Procesar items del carrito
            if request.user.is_authenticated:
                # Para usuarios autenticados
                for item in cart_items:
                    order.items.add(item)
                    producto = item.product
                    if producto.stock >= item.quantity:
                        producto.stock -= item.quantity
                        producto.save()
                        item.is_processed = True
                        item.save()
                    else:
                        order.delete()
                        messages.error(request, f'No hay suficiente stock de {producto.name}')
                        return redirect('shoppingCart:cart_detail')
            else:
                # Para usuarios no autenticados
                for item in cart_items:
                    producto = item['product']
                    quantity = item['quantity']
                    if producto.stock >= quantity:
                        cart_item = CartItem.objects.create(
                            product=producto,
                            quantity=quantity,
                            is_processed=True
                        )
                        order.items.add(cart_item)
                        producto.stock -= quantity
                        producto.save()
                    else:
                        order.delete()
                        messages.error(request, f'No hay suficiente stock de {producto.name}')
                        return redirect('shoppingCart:cart_detail')

            # Limpiar carrito
            if request.user.is_authenticated:
                CartItem.objects.filter(user=request.user, is_processed=False).delete()
            else:
                request.session['cart'] = {}
                request.session.modified = True  # Asegura que los cambios se guarden

            messages.success(request, 'Pedido realizado con éxito')
            return redirect('shoppingCart:order_confirmation')

        except Exception as e:
            logger.error(f"Error al procesar el pedido: {e}")
            if 'order' in locals():
                order.delete()
            messages.error(request, 'Error al procesar el pedido. Por favor, inténtelo de nuevo.')
            return redirect('shoppingCart:checkout_view')

    context = {
        'cart_items': cart_items,
        'precio_total': precio_total,
        'precio_total_con_envio': precio_total_con_envio,
        'shipping_cost': shipping_cost,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, 'checkout.html', context)

def order_confirmation(request):
     # Si el usuario está autenticado
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_processed=False)
        for item in cart_items:
            # Verificamos el stock antes de procesar el pedido
            product = item.product
            if product.stock >= item.quantity:
                # Actualizar el stock
                product.stock -= item.quantity
                product.save()

                # Marcamos el item como procesado
                item.is_processed = True
                item.save()
            else:
                # Si no hay suficiente stock
                messages.error(request, f'No hay suficiente stock para el producto {product.name}.')
                return redirect('shoppingCart:cart_detail')
        
        messages.success(request, "Gracias por tu compra. Tu carrito ha sido vaciado.")
    else:
        # Si el usuario no está autenticado, vaciamos el carrito de la sesión
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            if product.stock >= quantity:
                # Actualizamos el stock
                product.stock -= quantity
                product.save()
            else:
                # Si no hay suficiente stock
                messages.error(request, f'No hay suficiente stock para el producto {product.name}.')
                return redirect('shoppingCart:cart_detail')

        # Vaciamos el carrito de la sesión
        del request.session['cart']
        messages.success(request, "Gracias por tu compra. Tu carrito ha sido vaciado.")
    
    # Redirigir a la página de inicio o una página de agradecimiento
    return redirect('home')  # O cualquier otra página que quieras


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        if request.user.is_authenticated:
            # El usuario está autenticado, manejar en la base de datos
            try:
                cart_item = CartItem.objects.get(user=request.user, product_id=product_id, is_processed=False)

                # Reducir la cantidad o eliminar si es 1
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
                    product.stock += cart_item.quantity
                    product.save()   

                messages.success(request, f'{cart_item.product.name} eliminado del carrito.')
            except CartItem.DoesNotExist:
                messages.error(request, 'El producto no está en tu carrito.')
        else:
            # Usuario no autenticado: manejar en la sesión
            cart = request.session.get('cart', {})

            # Verificar si el producto está en el carrito
            if str(product_id) in cart:
                cart[str(product_id)] -= 1
                if cart[str(product_id)] <= 0:
                    del cart[str(product_id)]  # Eliminar el producto si su cantidad es 0

                # Actualizar el carrito en la sesión
                request.session['cart'] = cart
                request.session.modified = True  # Asegurar que los cambios se guarden
                 
            else:
                messages.error(request, 'El producto no está en tu carrito.')

        # Verificar el parámetro 'next' para redirigir a la página correspondiente
        next_url = request.POST.get('next', 'home')  # Redirige a 'home' por defecto
        return redirect(next_url)  # Redirige al home o al carrito según corresponda
    else:
        # Si no es un método POST, redirigir al home
        return redirect('home')
