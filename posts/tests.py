from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import User
from .models import Post
from .serializers import PostSerializer
from .permissions import IsOwner
from .views import CreatePostView


# Create your tests here.
class CreatePostViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('create-post')
    
    def test_create_post_success(self):
        data = {'text': 'Some normal text'}
        with patch('posts.utils.check_for_obscence', return_value=True):
            response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'Post created successfully!')
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().text, 'Some normal text')
    
    def test_create_post_with_obscene_content(self):
        data = {'text': 'Some obscene text'}
        with patch('posts.utils.check_for_obscence', return_value=False):
            response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Your post is obscene. The post will not be created.")
        self.assertEqual(Post.objects.count(), 0)
    
    def test_create_post_without_authentication(self):
        self.client.logout()
        data = {'text': 'This is a clean post'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)