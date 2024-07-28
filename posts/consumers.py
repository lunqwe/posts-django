import json
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Post
from .serializers import PostSerializer
from .tasks import get_posts_task

class PostConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    
    serializer_class = PostSerializer
    authentication_classes = (JWTAuthentication, )
    
    #default action to connect websocket
    async def connect(self):
        
        await self.channel_layer.group_add(
            'posts_group',
            self.channel_name
        )
        await self.accept()
        
    
    # action for load posts
    @action()
    async def get_posts(self, page_num: int, **kwargs):
        posts = get_posts_task.apply_async(args=[page_num]) # celery task to load data from db

        return await self.send(text_data=json.dumps({
            'event_type': 'display_post',
            'post': posts.get()
        }))
        
    # create post function (not @action because of api endpoint)
    async def add_post(self, event: dict):
        post = event['post']
        await self.send(text_data=json.dumps({
            'event_type': 'display_post',
            'post': post
        }))
    
    # action for close websocket connection
    @action()
    async def logout(self, **kwargs):
        await self.channel_layer.group_discard(
            'posts_group',
            self.channel_name
        )
        await self.close(1000)
    