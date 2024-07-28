import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.middleware import JWTAuthMiddleware
from posts import routing as posts_routing
from comments import routing as comments_routing


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            posts_routing.websocket_urlpatterns + comments_routing.websocket_urlpatterns
        )
    ),
})