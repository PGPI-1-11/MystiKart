from django.shortcuts import get_object_or_404, render, redirect
from product.models import Product
from shoppingCart.models import CartItem
from .forms import ShippingAddressForm 
from django.contrib import messages
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


def generate_tracking_id():
    """Genera un ID de seguimiento único con letras y números aleatorios."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))



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
    # Verifica si el usuario está autenticado para obtener su email
    if request.user.is_authenticated:
        user_email = request.user.email
    else:
        # Si el usuario no está autenticado, usa el correo que ingresó en el formulario
        user_email = request.POST.get('email')

    # Si no se proporciona un correo, muestra un mensaje de error
    if not user_email:
        messages.error(request, 'Por favor ingresa un correo electrónico válido.')
        return redirect('home')  # O a la página donde se pueda ingresar el correo

    # Verifica si el usuario está autenticado y obtiene los elementos del carrito
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user_id=request.user.id, is_processed=False)
    else:
        # Verifica que la sesión contenga un carrito con productos
        cart_session = request.session.get('cart', {})

        # Si la sesión tiene productos, convierte la lista de artículos
        if isinstance(cart_session, dict):
            cart_items = []
            for product_id, quantity in cart_session.items():
                try:
                    product = Product.objects.get(id=product_id)
                    cart_items.append({
                        'product': product,
                        'quantity': quantity
                    })
                except Product.DoesNotExist:
                    continue
        else:
            cart_items = []

    # Variables para la información del pedido
    precio_total = 0
    cart_items_for_order = []  # Esta lista almacenará las instancias de CartItem

    # Recorre los productos del carrito y calcula el total
    for item in cart_items:
        if isinstance(item, CartItem):
            # Para usuarios logueados, `item` es un CartItem
            product = item.product
            subtotal = product.price * item.quantity
            precio_total += subtotal
            cart_items_for_order.append(item)
        else:
            # Para usuarios no logueados, cada 'item' es un diccionario con producto y cantidad
            product = item['product']
            quantity = item['quantity']
            subtotal = product.price * quantity
            precio_total += subtotal

            # Crea un CartItem para agregarlo al pedido
            cart_item = CartItem(product=product, quantity=quantity, user=request.user if request.user.is_authenticated else None)
            cart_item.save()
            cart_items_for_order.append(cart_item)

    # Si el usuario está autenticado, creamos el pedido con su dirección y datos
    if request.user.is_authenticated:
        address = request.POST.get('address', '')
        tracking_id = generate_tracking_id()  # Genera un ID de seguimiento único
        order = Order.objects.create(
            user=request.user,
            address=address,
            email=user_email,
            precio_total=precio_total,
            shipping_cost=10.0,  # O calcular según corresponda
            id_tracking=tracking_id,  # Asigna el ID de seguimiento generado
            status=Order.StatusChoices.PROCESADO,  # Inicialmente, el estado es "Procesado"
            delivery_option=request.POST.get('delivery_option', 'Domicilio'),
            payment_option=request.POST.get('payment_option', 'contra_reembolso')
        )

        # Asocia los items del carrito al pedido
        order.items.set(cart_items_for_order)

        # Actualizamos el estado de los CartItems a 'procesado'
        CartItem.objects.filter(user_id=request.user.id, is_processed=False).update(is_processed=True)

    else:
        # Si el usuario no está autenticado, simplemente creamos el pedido como 'invitado'
        address = request.POST.get('address', '')
        tracking_id = generate_tracking_id()  # Genera un ID de seguimiento único
        order = Order.objects.create(
            user=None,  # No hay usuario, lo tratamos como un invitado
            address=address,
            email=user_email,
            precio_total=precio_total,
            shipping_cost=10.0,  # O calcular según corresponda
            id_tracking=tracking_id,  # Asigna el ID de seguimiento generado
            status=Order.StatusChoices.PROCESADO,  # Inicialmente, el estado es "Procesado"
            delivery_option=request.POST.get('delivery_option', 'Domicilio'),
            payment_option=request.POST.get('payment_option', 'contra_reembolso')
        )

        # Asociamos los productos desde la sesión al pedido
        for item in cart_items_for_order:
            order.items.add(item)

    # Define el contenido del email de confirmación
    subject = 'Confirmación de tu pedido en MystiKart'
    plain_message = (
        f"Gracias por tu pedido en MystiKart.\n"
        "Tu pedido ha sido confirmado exitosamente y está siendo procesado.\n\n"
        "Para ver el estado de tu pedido, utiliza el siguiente localizador:\n\n"
        f"Localizador: {order.id_tracking}\n\n"
        "Saludos,\n"
        "El equipo de MystiKart"
    )
    from_email = 'MystiKart <mystikartpgpi@gmail.com>'
    to_email = [user_email]

    # Enviar el email de confirmación
    try:
        send_mail(subject, plain_message, from_email, to_email)
        if request.user.is_authenticated:
            messages.success(request, 'Se ha enviado un correo de confirmación a tu dirección registrada.')
        else:
            messages.success(request, 'Se ha enviado un correo de confirmación a la dirección proporcionada.')
    except Exception as e:
        messages.error(request, f'No se pudo enviar el correo: {e}')

    # Renderiza la página de confirmación
    return render(request, 'confirmation.html', {'order': order, 'is_confirmation_page': True})



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
