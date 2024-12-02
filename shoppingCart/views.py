import secrets
import logging
from django.shortcuts import get_object_or_404, render, redirect
from MystiKart import settings
from order.models import Order
from product.models import Product
from shoppingCart.models import CartItem
from .forms import ShippingAddressForm 
from django.contrib import messages
from .models import ShippingAddress
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from order.models import Order
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import random
import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


def add_to_cart(request, product_id):
    if request.method == 'POST':
        # Obtener el producto
        product = get_object_or_404(Product, id=product_id)
        # Obtener la cantidad solicitada
        quantity = int(request.POST.get('quantity', 1))

        # Comprobar si el usuario está autenticado
        if request.user.is_authenticated:
            # Usuario autenticado: manejar en base de datos
            cart, created = CartItem.objects.get_or_create(
                user=request.user, 
                product=product, 
                is_processed=False, 
                defaults={'quantity': 0}
            )

            # Verificar stock disponible
            if cart.quantity + quantity > product.stock:
                messages.error(request, 'No hay suficiente stock disponible.')
                return redirect('home')

            # Actualizar la cantidad del producto
            cart.quantity += quantity
            cart.save()
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

        # Redirigir de vuelta al inicio o donde corresponda
        messages.success(request, f'{product.name} se ha agregado al carrito.')
        return redirect('home')  # Cambia 'home' por la página adecuada
    else:
        return redirect('home')


def generate_tracking_id():
    """Genera un ID de seguimiento único con letras y números aleatorios."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def cart_detail(request):
    form = ShippingAddressForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        shipping_address = form.save(commit=False)

        if request.user.is_authenticated:
            # Guardar la dirección para el usuario autenticado
            shipping_address.user = request.user
            shipping_address.save()
            messages.success(request, 'Dirección confirmada.')
        else:
            # Guardar los datos en la sesión para usuarios no autenticados
            request.session['order_shipping_data'] = {
                'full_name': shipping_address.full_name,
                'address': shipping_address.address,
                'city': shipping_address.city,
                'postal_code': shipping_address.postal_code,
                'country': shipping_address.country,
            }
            messages.success(request, 'Dirección guardada en la sesión.')

        # Redirigir al proceso de pago
        return redirect('shoppingCart:checkout_view')  

    cart_items = []
    precio_total = 0
    precio_total_con_envio = 0

    costo_envio = 10  # Valor fijo de ejemplo

    if request.user.is_authenticated:
        # Cargar los CartItem del usuario autenticado
        user_cart_items = CartItem.objects.filter(user=request.user, is_processed=False)
        for item in user_cart_items:
            subtotal = item.product.price * item.quantity
            precio_total += subtotal
            cart_items.append(item)
    else:
        # Manejo del carrito en la sesión
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

    # Aplicar costo de envío
    if precio_total < 100:  # Envío gratuito si el total es mayor o igual a 100
        precio_total_con_envio = precio_total + costo_envio
    else:
        precio_total_con_envio = precio_total

    return render(request, 'cart_detail.html', {
        'cart_items': cart_items,
        'precio_total': precio_total,
        'precio_total_con_envio': precio_total_con_envio,
        'form': form,
        'costo_envio': costo_envio if precio_total < 100 else 0,
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

        if not address:
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
                    messages.error(request, 'Error al procesar el pago: Token no válido')
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
    # Obtener el carrito del usuario
    cart_items_for_order = []
    precio_total = 0
    shipping_address = None
    user_email = request.user.email if request.user.is_authenticated else request.POST.get('email')

    if not user_email:
        messages.error(request, 'Por favor ingresa un correo electrónico válido.')
        return redirect('home')

    # Obtener los productos del carrito
    if request.user.is_authenticated:
        # Si el usuario está autenticado, obtener el carrito asociado
        cart_items = CartItem.objects.filter(user=request.user, is_processed=False)
    else:
        # Si el usuario no está autenticado, obtener el carrito desde la sesión
        cart_session = request.session.get('cart', {})
        cart_items = []
        if isinstance(cart_session, dict):
            for product_id, quantity in cart_session.items():
                try:
                    product = Product.objects.get(id=product_id)
                    cart_items.append({
                        'product': product,
                        'quantity': quantity
                    })
                except Product.DoesNotExist:
                    continue

    # Procesar los productos del carrito
    for item in cart_items:
        if isinstance(item, CartItem):
            product = item.product
            if product.stock >= item.quantity:
                subtotal = product.price * item.quantity
                precio_total += subtotal
                cart_items_for_order.append(item)
                product.stock -= item.quantity
                product.save()
                item.is_processed = True
                item.save()
            else:
                messages.error(request, f'No hay suficiente stock para el producto {product.name}.')
                return redirect('shoppingCart:cart_detail')
        else:
            product = item['product']
            quantity = item['quantity']
            if product.stock >= quantity:
                subtotal = product.price * quantity
                precio_total += subtotal
                product.stock -= quantity
                product.save()
                cart_item = CartItem(product=product, quantity=quantity,
                                     user=request.user if request.user.is_authenticated else None)
                cart_item.save()
                cart_items_for_order.append(cart_item)
            else:
                messages.error(request, f'No hay suficiente stock para el producto {product.name}.')
                return redirect('shoppingCart:cart_detail')

    # Recuperar o crear una dirección de envío
    shipping_address_text = ""
    if request.user.is_authenticated:
        # Si el usuario está autenticado, obtener su dirección de envío
        shipping_address = ShippingAddress.objects.filter(user=request.user).latest('id')
        shipping_address_text = (
            "Datos de envío:\n"
            f"Calle: {shipping_address.address}, {shipping_address.postal_code},\n"
            f"Ciudad: {shipping_address.city},\n"
            f"País: {shipping_address.country}"
        )
    else:
        # Si el usuario no está autenticado, usar los datos de la sesión (si existen)
        order_data = request.session.get('order_shipping_data')
        if order_data:
            shipping_address = ShippingAddress(
                full_name=order_data.get('full_name'),
                address=order_data.get('address'),
                city=order_data.get('city'),
                postal_code=order_data.get('postal_code'),
                country=order_data.get('country')
            )
            shipping_address.save()
            shipping_address_text = (
                "Datos de envío:\n"
                f"Calle: {shipping_address.address}, {shipping_address.postal_code}\n"
                f"Ciudad: {shipping_address.city},\n"
                f"País: {shipping_address.country}"
            )

    # Crear el pedido
    tracking_id = generate_tracking_id()  # Genera un ID único para el seguimiento del pedido
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        address=shipping_address_text,  # Puedes usar un campo texto o un modelo para la dirección
        email=user_email,
        precio_total=precio_total,
        shipping_cost=10.0,  # Asume un costo fijo de envío o aplica lógica según el pedido
        id_tracking=tracking_id,
        status=Order.StatusChoices.PROCESADO,  # O el estado correspondiente
        delivery_option=request.POST.get('delivery_option', 'Domicilio'),  # Se agrega la opción de entrega
        payment_option=request.POST.get('payment_option', 'contra_reembolso')  # Se agrega la opción de pago
    )

    # Relacionar los items del carrito con el pedido
    order.items.set(cart_items_for_order)

    product_list = "\n".join([f"- {item.product.name} (x{item.quantity})" for item in cart_items_for_order])

    # Limpiar el carrito de la sesión si el usuario no está autenticado
    if not request.user.is_authenticated:
        request.session.pop('cart', None)

    # Calcular el total a pagar (precio total + costo de envío)
    if precio_total > 100.0:
        total_a_pagar = precio_total  # Si el total es mayor a 100€, no se añade el costo de envío
    else:
        total_a_pagar = precio_total + 10.0  # Si el total es menor o igual a 100€, añadir 10€ de envío

    # Enviar correo de confirmación al cliente
    subject = 'Confirmación de tu pedido en MystiKart'
    
    # Se genera un mensaje detallado
    plain_message = (
        f"Estimado/a {shipping_address.full_name},\n\n"
        "Gracias por tu pedido en MystiKart.\n"
        "Tu pedido ha sido confirmado exitosamente y está siendo procesado.\n\n"
        f"{shipping_address_text}\n\n"
        "Productos incluidos:\n"
        f"{product_list}\n\n"
        f"Total a pagar: {total_a_pagar}€\n\n"
        f"Metodo de entrega: {order.get_delivery_option_display()}\n"
        f"Metodo de pago: {order.get_payment_option_display()}\n\n"
        "Para ver el estado de tu pedido, utiliza el siguiente localizador:\n\n" +
        f"Localizador: {order.id_tracking}\n\n"
        "Saludos,\nMystiKart"
    )

    from_email = 'MystiKart <mystikartpgpi@gmail.com>'
    to_email = [user_email]

    try:
        send_mail(subject, plain_message, from_email, to_email)
        messages.success(request, 'Se ha enviado un correo de confirmación a tu dirección proporcionada.')
    except Exception as e:
        messages.error(request, f'No se pudo enviar el correo: {e}')

    return render(request, 'confirmation.html', {'order': order, 'is_confirmation_page': True})


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        if request.user.is_authenticated:
            # El usuario está autenticado, manejar en la base de datos
            try:
                cart = CartItem.objects.get(user=request.user, product_id=product_id, is_processed=False)

                remove_all = request.POST.get('remove_all', False)  # Detecta si es "eliminar todo"
                
                if remove_all:
                    cart.delete()
                else:
                    cart.quantity -= 1
                    if cart.quantity <= 0:
                        cart.delete()  # Eliminar el producto si su cantidad es 0
                    else:
                        cart.save()

                messages.success(request, f'{cart.product.name} eliminado del carrito.')
            except CartItem.DoesNotExist:
                messages.error(request, 'El producto no está en tu carrito.')
        else:
            # Usuario no autenticado: manejar en la sesión
            cart = request.session.get('cart', {})

            # Verificar si el producto está en el carrito
            if str(product_id) in cart:
                # Verificar si se quiere eliminar todo
                remove_all = request.POST.get('remove_all', False)  # Detecta si es "eliminar todo"

            # Verificar si el producto está en el carrito
            if str(product_id) in cart:
                if remove_all:
                    del cart[str(product_id)]  # Eliminar el producto
                else:
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