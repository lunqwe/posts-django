import json
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Comment
from .serializers import CommentSerializer
from .tasks import get_comments


class CommentsConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication, )
    
    #default action to connect websocket
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.room_group_name = f'post_{self.post_id}'
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        
    
    # action for load comments
    @action()
    async def get_comments(self, page_num: int, **kwargs):
        comments = get_comments.apply_async(args=[page_num, self.post_id]) # celery task to load data from db

        return await self.send(text_data=json.dumps({
            'event_type': 'display_comment',
            'comment': comments.get()
        }))
        
    # create comment function (not @action because of api endpoint)
    async def add_comment(self, event: dict):
        comment = event['comment']
        await self.send(text_data=json.dumps({
            'event_type': 'display_comment',
            'comment': comment
        }))
    
    # action for close websocket connection
    @action()
    async def logout(self, **kwargs):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.close(1000)
    