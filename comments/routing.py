from django.urls import re_path
from .consumers import CommentsConsumer

websocket_urlpatterns = [
    re_path(r'ws/posts/(?P<post_id>\d+)/comments/$', CommentsConsumer.as_asgi()),
]