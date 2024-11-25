from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from product.models import Product, Category, Brand

class ProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(email='email@email.com', password='useruser', is_staff=True, is_superuser=True)
        self.client.login(email='email@email.com', password='useruser')
        self.category = Category.objects.create(name='Test Category')
        self.brand = Brand.objects.create(name='Test Brand')

    def test_home_view(self):
        response = self.client.get(reverse('product:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')


    def test_product_info(self):
        product = Product.objects.create(name='Test Product', price=10.0, brand=self.brand, category=self.category)
        product.image = 'media/item_images/image.jpg'
        product.save()

        response = self.client.get(reverse('product:product_info', args=[product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info.html')