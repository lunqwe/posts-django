from django.urls import path, re_path

from .consumers import PostConsumer


websocket_urlpatterns = [
    path('ws/posts/', PostConsumer.as_asgi()),
]