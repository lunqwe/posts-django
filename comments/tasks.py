from celery_app import app
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from django.core.paginator import Paginator
from django.http import Http404
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from django.core.cache import cache

from accounts.models import User
from posts.models import Post
from .models import Comment
from .serializers import CommentSerializer
from posts.utils import check_for_obscence

# cache clear function
def clear_comments_cache():
    cache_keys_to_clear = [
        f'comments_page_{page_num}'
        for page_num in range(1, 100)
    ]
    cache.delete_many(cache_keys_to_clear)


# celery task for creating comment & notify websocket users
@app.task()
@transaction.atomic
def create_comment(owner_id: int, comment_data: dict, *args):
    comment_text = comment_data.get('text')
    if check_for_obscence(comment_text):
        user = User.objects.get(id=owner_id)
        comment_data.pop('owner')
        post_id = comment_data.pop('post')
        post = Post.objects.get(id=post_id) 
        comment = Comment.objects.create(owner=user, post=post, **comment_data)
        comment_data = CommentSerializer(comment).data
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
                    f"post_{post.id}",
                    {
                        'type': 'add_comment',
                        'comment': {
                            'username': comment.owner.username,
                            'text': comment.text,
                        }
                    }
                )
        return {'status':'success', 'detail': 'Comment created successfully!', 'comment': comment_data}
    else:
        return {'status': 'fail', 'detail': 'Your comment is obscene. The comment will not be created.'}

# celery task to load comments
@app.task()
def get_comments(page_num: int, post_id: int) -> list:
    queryset = Comment.objects.filter(post_id=post_id).order_by('created_at')[::-1]
    paginator = Paginator(queryset, 25)
    result = paginator.get_page(page_num)
    comments = []
    for comment in result:
        comments.append({
            'id': comment.id,
            'username': comment.owner.username,
            'text': comment.text
        })
        
    return comments
