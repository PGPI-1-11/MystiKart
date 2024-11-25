from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from product.models import Product, Category, Brand
from django.core.files.uploadedfile import SimpleUploadedFile
from core.views import home


class ProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(email='email@email.com', password='useruser', is_staff=True, is_superuser=True)
        self.client.login(email='email@email.com', password='useruser')
        self.category = Category.objects.create(name='Test Category')
        self.brand = Brand.objects.create(name='Test Brand')
        self.image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        self.product = Product.objects.create(name='Test Product', price=10.0, brand=self.brand, category=self.category, image=self.image)
        self.url = reverse('product:home')

    def test_home_view(self):
        response = self.client.get(reverse('product:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_product_info(self):
        response = self.client.get(reverse('product:product_info', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info.html')

    def test_home_view_renders_correct_template(self):
        response = self.client.get(reverse('product:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_view_loads_products(self):
        response = self.client.get(reverse('product:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context)

    def test_home_view_filters_by_category(self):
        response = self.client.get(reverse('product:home'), {'category': self.category.name})
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context)

    def test_home_view_filters_by_brand(self):
        response = self.client.get(reverse('product:home'), {'brand': self.brand.name})
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context)

    def test_home_view_filters_by_query(self):
        response = self.client.get(reverse('product:home'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context)

    def test_home_view_handles_empty_cart(self):
        self.client.session['cart'] = {}
        self.client.session.save()
        response = self.client.get(reverse('product:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context)

    def test_home_view_handles_invalid_product_in_cart(self):
        self.client.session['cart'] = {999: 1}  # Producto inexistente
        self.client.session.save()
        response = self.client.get(reverse('product:home'))
        self.assertNotIn(999, self.client.session.get('cart', {}))

def test_home_view_handles_no_products(self):
    Product.objects.all().delete()
    
    response = self.client.get(reverse('product:home'))
    
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.context.get('no_products', False))


