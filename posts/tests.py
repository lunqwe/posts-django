from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import User
from .models import Post



# Create your tests here.
class CreatePostViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('create-post')
    
    @patch('posts.views.create_post.apply_async')
    @patch('posts.utils.check_for_obscence', return_value=True)
    def test_create_post_success(self, mock_check_obscence, mock_create_post):
        data = {'text': 'Some normal text'}
        mock_task_result = mock_create_post.return_value
        mock_task_result.get.return_value = {'status':'success', 'detail': 'Post created successfully!', 'post': {'id': 1, 'text': 'Some normal text'}}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'Post created successfully!')
        mock_create_post.assert_called_once_with(args=[self.user.id, data])
        mock_task_result.get.assert_called_once()
    
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
        
class RetrievePostViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create a post for testing
        self.post = Post.objects.create(text='This is a test post', owner=self.user)
        self.url = reverse('post-details', kwargs={'id': self.post.id}) 

    def test_retrieve_post_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.post.id)
        self.assertEqual(response.data['text'], self.post.text)
    
    def test_retrieve_non_existent_post(self):
        url = reverse('post-details', kwargs={'id': 9999})  # An ID that does not exist
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ensure_correct_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.post.id)
        self.assertEqual(response.data['text'], self.post.text)
        self.assertEqual(response.data['owner'].get('id'), self.user.id)
        
        
class ListPostViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create some posts for testing
        self.post1 = Post.objects.create(text='Post 1', owner=self.user)
        self.post2 = Post.objects.create(text='Post 2', owner=self.user)
        self.post3 = Post.objects.create(text='Some Text', owner=self.user)
        
        self.url = reverse('post-list')

    def test_retrieve_all_posts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 3) 

    def test_filter_posts(self):
        response = self.client.get(self.url, {'text__icontains': 'Post'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 2) 

    def test_ensure_correct_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for post in response.data.get('results'):
            self.assertIn('id', post)
            self.assertIn('text', post)
            self.assertIn('owner', post)
            

class UpdatePostViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@gmail.com')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpassword', email='otheruser@gmail.com')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.post = Post.objects.create(text='Original post', owner=self.user)
        self.url = reverse('post-update', kwargs={'id': self.post.id})

    def test_update_post_success(self):
        data = {'text': 'Updated post'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Updated post')
    
    def test_update_post_with_invalid_data(self):
        data = {'text': ''}  # Assuming text field cannot be empty
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_post_without_authentication(self):
        self.client.logout()
        data = {'text': 'Updated post'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_post_by_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        data = {'text': 'Updated post'}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        

class DeletePostViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@gmail.com')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpassword', email='otheruser@gmail.com')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.post = Post.objects.create(text='Post to delete', owner=self.user)
        self.url = reverse('post-delete', kwargs={'id': self.post.id}) 

    def test_delete_post_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())
    
    def test_delete_post_without_authentication(self):
        self.client.logout()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_delete_post_by_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())