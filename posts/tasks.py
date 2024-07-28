from celery_app import app
from django.core.paginator import Paginator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from django.http import Http404
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from accounts.models import User
from .serializers import PostSerializer
from posts.utils import check_for_obscence
from .models import Post


@app.task()
def get_posts_task(page_num: int) -> list:
    print(1)
    try:
        queryset = Post.objects.all().order_by('created_at')[::-1]
        paginator = Paginator(queryset, 25)
        result = paginator.get_page(page_num)
        posts = []
        for post in result:
            posts.append({
                'id': post.id,
                'username': post.owner.username,
                'text': post.text
            })
        return posts
    except Exception as e:
        print(f"Error in get_posts task: {e}")
        
        
@app.task()
@transaction.atomic
def create_post(owner_id: int, post_data: dict, *args):
    post_text = post_data.get('text')
    if check_for_obscence(post_text):
        user = User.objects.get(id=owner_id)
        post = Post.objects.create(owner=user, **post_data)
        post_data = PostSerializer(post).data
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
                    'posts_group',
                    {
                        'type': 'add_post',
                        'post': {
                            'username': post.owner.username,
                            'text': post.text,
                        }
                    }
                )
        return {'status':'success', 'detail': 'Post created successfully!', 'post': post_data}
    else:
        return {'status': 'fail', 'detail': 'Your post is obscene. The post will not be created.'}