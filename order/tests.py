from django.test import TestCase
from django.urls import reverse
from order.models import Order

class OrderSearchViewTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            id_tracking='12345', 
            status='procesado', 
            precio_total=100.0
        )

    def test_order_search_valid_tracking_id(self):
        response = self.client.get(reverse('order_search'), {'id_tracking': '12345'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orderStatus.html')
        self.assertIn('order', response.context)
        self.assertIn('order_progress', response.context)
        self.assertIn('state_map', response.context)

    def test_order_search_invalid_tracking_id(self):
        response = self.client.get(reverse('order_search'), {'id_tracking': 'invalid'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'El ID de seguimiento no existe.')

    def test_order_search_no_tracking_id(self):
        response = self.client.get(reverse('order_search'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

class OrderDetailViewTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            id=1,
            id_tracking='12345', 
            status='procesado', 
            precio_total=100.0
        )

    def test_order_detail_valid_order_id(self):
        response = self.client.get(reverse('order_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orderStatus.html')
        self.assertIn('order', response.context)
        self.assertIn('order_progress', response.context)
        self.assertIn('state_map', response.context)

    def test_order_detail_invalid_order_id(self):
        response = self.client.get(reverse('order_detail', args=[999]))
        self.assertEqual(response.status_code, 404)