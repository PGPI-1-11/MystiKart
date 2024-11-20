from django.test import TestCase, Client
from django.urls import reverse
from custom_user.forms import MyAuthForm, RegistrationForm
from custom_user.models import User

class UserAdminViewTest(TestCase):
    def setUp(self):
        # Crear usuarios de prueba
        self.admin_user = User.objects.create_user(
            email='admin@admin.com',
            password='password123',
            is_staff=True,
        )

        self.normal_user = User.objects.create_user(
            email='user@user.com',
            password='password123',
            is_staff=False,
        )

        self.client = Client()

    def test_staff_access_user_admin_view(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('user_admin_view'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lista de Usuarios')

    def test_non_staff_cannot_access_user_admin_view(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse('user_admin_view'), follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Lista de Usuarios')

class RegistrationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('registro')
        self.login_url = reverse('login')
        self.valid_user_data = {
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }

    def test_get_registration_page(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

    def test_successful_registration(self):
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertTrue(
            User.objects.filter(email='test@example.com').exists()
        )

    def test_invalid_registration_password_mismatch(self):
        invalid_data = self.valid_user_data.copy()
        invalid_data['password2'] = 'wrongpassword'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(email='test@example.com').exists()
        )

class CustomLoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )

    def test_get_login_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_successful_login(self):
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpassword123'
        }, follow=True)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login_wrong_password(self):
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)