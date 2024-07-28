from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

from accounts.models import User
from posts.models import Post
from .models import Comment
from .serializers import CreateCommentSerializer

class CreateCommentViewTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@gmail.com')
        self.post = Post.objects.create(owner=self.user, text='Some text')
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.url = reverse('create-comment') 
        
    @patch('comments.tasks.create_comment.apply_async')
    @patch('posts.utils.check_for_obscence', return_value=True)
    def test_create_comment_success(self, mock_check_obscence, mock_create_post):
        data = {'text': 'Some normal text', 'owner': self.user.id, 'post': self.post.id}
        mock_task_result = mock_create_post.return_value
        mock_task_result.get.return_value = {'status':'success', 'detail': 'Comment created successfully!', 'comment': {'id': self.post.id, 'text': 'Some normal text'}}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'Comment created successfully!')

    @patch('comments.tasks.create_comment.apply_async')
    @patch('posts.utils.check_for_obscence', return_value=True)
    def test_create_comment_obscene(self, mock_check_obscence, mock_create_post):
        data = {'text': 'Some obscene text', 'owner': self.user.id, 'post': self.post.id}
        mock_task_result = mock_create_post.return_value
        mock_task_result.get.return_value = {'status': 'fail', 'detail': 'Your comment is obscene. The comment will not be created.'}
        with patch('posts.utils.check_for_obscence', return_value=False):
            response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Your comment is obscene. The comment will not be created.")
        self.assertEqual(Comment.objects.count(), 0)

    def test_create_comment_unauthenticated(self):
        self.client.credentials()
        data = {
            'text': 'This is a test comment.',
            'post': 1
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
class RetrieveCommentViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.post = Post.objects.create(owner=self.user, text='Some text')
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.comment = Comment.objects.create(owner=self.user, text='This is a test comment.', post=self.post)
        self.url = reverse('retrieve-comment', kwargs={'id': self.comment.id}) 

    def test_retrieve_comment_success(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.comment.id)
        self.assertEqual(response.data['text'], self.comment.text)

    def test_retrieve_comment_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_nonexistent_comment(self):
        url = reverse('retrieve-comment', kwargs={'id': 999})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        
class ListCommentViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.post = Post.objects.create(owner=self.user, text='Some text')
        self.comment1 = Comment.objects.create(owner=self.user, text='This is the first test comment.', post=self.post)
        self.comment2 = Comment.objects.create(owner=self.user, text='This is the second test comment.', post=self.post)
        
        self.url = reverse('list-comments')

    def test_list_comments_success(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 2)
        self.assertEqual(response.data.get('results')[0]['id'], self.comment1.id)
        self.assertEqual(response.data.get('results')[1]['id'], self.comment2.id)

    def test_list_comments_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_comments_with_filters(self):
        response = self.client.get(self.url, {'text__icontains': 'first'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0]['id'], self.comment1.id)
        self.assertEqual(response.data.get('results')[0]['text'], self.comment1.text)
        
        
class UpdateCommentViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@gmail.com')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpassword', email='othertest@gmail.com')
        self.post = Post.objects.create(owner=self.user, text='test text')
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.comment = Comment.objects.create(
            owner=self.user,
            text='This is a test comment.',
            post=self.post
        )
        
        self.url = reverse('update-comment', args=[self.comment.id])

    def test_update_comment_success(self):
        updated_data = {'text': 'This is an updated test comment.', 'post': self.post.id}
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'This is an updated test comment.')

    def test_update_comment_unauthenticated(self):
        self.client.credentials()
        updated_data = {'text': 'This is an updated test comment.'}
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_not_owner(self):
        refresh = RefreshToken.for_user(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        updated_data = {'text': 'This is an updated test comment.'}
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
class DeleteCommentViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@gmail.com')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpassword', email='othertest@gmail.com')
        self.post = Post.objects.create(owner=self.user, text='test text')
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.comment = Comment.objects.create(
            owner=self.user,
            text='This is a test comment.',
            post=self.post
        )
        self.url = reverse('delete-comment', args=[self.comment.id])

    def test_delete_comment_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_unauthenticated(self):
        self.client.credentials()  # Remove the token to simulate an unauthenticated request
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_comment_not_owner(self):
        refresh = RefreshToken.for_user(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())