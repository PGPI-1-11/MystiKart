from django.test import Client
from django.urls import reverse
from product.models import Category, Product


class SearchProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")
        self.brand = Brand.objects.create(name="Brand 1")
        
        self.product1 = Product.objects.create(
            name="Product One", price=10.0, category=self.category1, brand=self.brand
        )
        self.product2 = Product.objects.create(
            name="Product Two", price=20.0, category=self.category2, brand=self.brand
        )
        self.product3 = Product.objects.create(
            name="Another Product", price=15.0, category=self.category1, brand=self.brand
        )
        self.url = reverse('product:search_product')

    def test_search_without_filters(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['products'].order_by('id'),
            Product.objects.all().order_by('id'),
            transform=lambda x: x
        )

    def test_search_with_query(self):
        response = self.client.get(self.url, {'q': 'Product'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['products'].order_by('id'),
            Product.objects.filter(name__icontains='Product').order_by('id'),
            transform=lambda x: x
        )

    def test_search_with_category(self):
        response = self.client.get(self.url, {'category': self.category1.id})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['products'].order_by('id'),
            Product.objects.filter(category=self.category1).order_by('id'),
            transform=lambda x: x
        )

    def test_search_with_query_and_category(self):
        response = self.client.get(self.url, {'q': 'Product', 'category': self.category1.id})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['products'].order_by('id'),
            Product.objects.filter(name__icontains='Product', category=self.category1).order_by('id'),
            transform=lambda x: x
        )

    def test_search_empty_result(self):
        response = self.client.get(self.url, {'q': 'Nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['products'].order_by('id'),
            Product.objects.none().order_by('id'),
            transform=lambda x: x
        )

    def test_context_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context)
        self.assertIn('query', response.context)
        self.assertIn('categoria_id', response.context)
        self.assertIn('categories', response.context)
        self.assertQuerySetEqual(
            response.context['categories'].order_by('id'),
            Category.objects.all().order_by('id'),
            transform=lambda x: x
        )