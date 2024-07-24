from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
from .serializers import CreateUserSerializer
from .models import User

class CreateUserViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('create_user')
        self.valid_user_data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'newuser@example.com'
        }
        self.invalid_user_data = {
            'username': '',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'newuser@example.com'
        }

    def test_create_user_success(self):
        response = self.client.post(self.url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_create_user_invalid_data(self):
        response = self.client.post(self.url, self.invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertFalse(User.objects.filter(username='').exists())


class LoginUserViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.user = User.objects.create_user(email='test@gmail.com', username='test', password='testpassword123')
        self.valid_login_data = {
            'email': 'test@gmail.com',
            'password': 'testpassword123'
        }
        self.invalid_login_data = {
            'email': 'test@gmail.com',
            'password': 'wrongpassword'
        }

    def test_login_user_success(self):
        response = self.client.post(self.url, self.valid_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['user']['id'], self.user.id)

    def test_login_user_invalid_credentials(self):
        response = self.client.post(self.url, self.invalid_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')