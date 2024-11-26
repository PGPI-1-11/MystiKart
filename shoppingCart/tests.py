from django.test import TestCase, Client
from django.urls import reverse
from custom_user.models import User
from shoppingCart.models import CartItem, ShippingAddress
from product.models import Product, Category, Brand

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
        # Enviar una solicitud POST para añadir el producto al carrito
        response = self.client.post(reverse('shoppingCart:add_to_cart', args=[self.product.id]), {'quantity': 1})
        self.assertEqual(response.status_code, 302)  # Redirección

        # Verificar que el producto está en el carrito de la sesión
        session = self.client.session
        cart = session.get('cart', {})
        self.assertIn(str(self.product.id), cart)
        self.assertEqual(cart[str(self.product.id)], 1)

    def test_cart_detail_authenticated_user(self):
        # Loguear al usuario
        self.client.login(email="testuser@example.com", password="password")

        # Crear un CartItem para el usuario
        CartItem.objects.create(user=self.user, product=self.product, quantity=2, is_processed=False)

        # Acceder a la vista de detalles del carrito
        response = self.client.get(reverse('shoppingCart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart_detail.html')

        # Verificar que el carrito contiene los items correctos
        cart_items = response.context['cart_items']
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0].quantity, 2)
        self.assertEqual(cart_items[0].product, self.product)

    def test_cart_detail_unauthenticated_user(self):
        # Añadir producto al carrito
        session = self.client.session
        session['cart'] = {str(self.product.id): 2}
        session.save()

        # Acceder a la vista de detalles del carrito
        response = self.client.get(reverse('shoppingCart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart_detail.html')

        # Verificar el contenido del carrito
        cart_items = response.context['cart_items']
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['product'].id, self.product.id)
        self.assertEqual(cart_items[0]['quantity'], 2)