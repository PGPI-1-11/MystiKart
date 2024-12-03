from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from custom_user.models import User
from shoppingCart.models import CartItem, ShippingAddress
from product.models import Product, Category, Brand


User = get_user_model()

class CartViewsTest(TestCase):
    def setUp(self):
        # Crear un cliente para simular peticiones
        self.client = Client()

        self.category = Category.objects.create(name="Test Category")
        self.brand = Brand.objects.create(name="Test Brand")

        # Crear un producto de prueba
        self.product = Product.objects.create(
            name="Test Product",
            price=10.0,
            stock=100,
            category=self.category,
            brand=self.brand
        )

        # Crear un usuario para las pruebas autenticadas
        self.user = User.objects.create_user(email="testuser@example.com", password="password")

    def test_add_to_cart(self):
        response = self.client.post(reverse('shoppingCart:add_to_cart', args=[self.product.id]), {'quantity': 1})
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        cart = session.get('cart', {})
        self.assertIn(str(self.product.id), cart)
        self.assertEqual(cart[str(self.product.id)], 1)

    def test_cart_detail_authenticated_user(self):
        self.client.login(email="testuser@example.com", password="password")
        CartItem.objects.create(user=self.user, product=self.product, quantity=2, is_processed=False)
        response = self.client.get(reverse('shoppingCart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart_detail.html')
        cart_items = response.context['cart_items']
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0].quantity, 2)
        self.assertEqual(cart_items[0].product, self.product)

    def test_cart_detail_unauthenticated_user(self):
        session = self.client.session
        session['cart'] = {str(self.product.id): 2}
        session.save()
        response = self.client.get(reverse('shoppingCart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart_detail.html')
        cart_items = response.context['cart_items']
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['quantity'], 2)
        self.assertEqual(cart_items[0]['product'], self.product)

    def test_remove_from_cart_authenticated_user(self):
        self.client.login(email="testuser@example.com", password="password")
        CartItem.objects.create(user=self.user, product=self.product, quantity=2, is_processed=False)
        response = self.client.post(reverse('shoppingCart:remove_from_cart', args=[self.product.id]), {'remove_all': True})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CartItem.objects.filter(user=self.user, product=self.product).exists())

    def test_remove_from_cart_unauthenticated_user(self):
        session = self.client.session
        session['cart'] = {str(self.product.id): 2}
        session.save()
        response = self.client.post(reverse('shoppingCart:remove_from_cart', args=[self.product.id]), {'remove_all': True})
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        cart = session.get('cart', {})
        self.assertNotIn(str(self.product.id), cart)

    def test_checkout_view_empty_cart(self):
        # Loguear al usuario
        self.client.login(email="testuser@example.com", password="password")

        # Intentar acceder a la vista de checkout con el carrito vacío
        response = self.client.get(reverse('shoppingCart:checkout_view'))
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertRedirects(response, reverse('shoppingCart:cart_detail'))

    def test_checkout_view_with_items_authenticated_user(self):
        # Loguear al usuario
        self.client.login(email="testuser@example.com", password="password")

        # Crear un CartItem para el usuario
        CartItem.objects.create(user=self.user, product=self.product, quantity=2, is_processed=False)

        # Acceder a la vista de checkout
        response = self.client.get(reverse('shoppingCart:checkout_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout.html')

        # Verificar el contenido del carrito en la vista
        self.assertEqual(response.context['precio_total'], 20.0)
        self.assertEqual(response.context['precio_total_con_envio'], 30.0)  # Incluye costo de envío

    def test_order_confirmation_authenticated_user(self):
        self.client.login(email="testuser@example.com", password="password")
        CartItem.objects.create(user=self.user, product=self.product, quantity=2, is_processed=False)
        ShippingAddress.objects.create(
            user=self.user,
            full_name="Test User",
            address="123 Test St",
            city="Test City",
            postal_code="12345",
            country="Test Country"
        )
        response = self.client.post(reverse('shoppingCart:order_confirmation'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirmation.html')

    def test_order_confirmation_unauthenticated_user(self):
        session = self.client.session
        session['cart'] = {str(self.product.id): 2}
        session['order_shipping_data'] = {
            'full_name': 'Test User',
            'address': '123 Test St',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'Test Country'
        }
        session.save()
        response = self.client.post(reverse('shoppingCart:order_confirmation'), {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirmation.html')

    def test_checkout_with_authenticated_user(self):
        self.client.login(email='testuser@example.com', password='password')
        response = self.client.post(reverse('shoppingCart:checkout_view'), {
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'country': 'Test Country',
            'payment_option': 'tarjeta',
            'stripeToken': 'tok_visa'
        })
        self.assertEqual(response.status_code, 302)  # Esperar una redirección
        self.assertRedirects(response, reverse('shoppingCart:cart_detail'))  
        
    def test_checkout_with_insufficient_stock(self):
        self.client.login(username='testuser', password='12345')
        self.product.stock = 0
        self.product.save()
        response = self.client.post(reverse('shoppingCart:checkout_view'), {
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'country': 'Test Country',
            'payment_option': 'tarjeta',
            'stripeToken': 'tok_visa'
        })
        self.assertEqual(response.status_code, 302)  # Esperar una redirección
        self.assertRedirects(response, reverse('shoppingCart:cart_detail'))  # Verificar la redirección a la página del carrito