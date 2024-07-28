from rest_framework import serializers
from .models import Post
from accounts.models import User

class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['text']
        
class PostOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class PostSerializer(serializers.ModelSerializer):
    owner = PostOwnerSerializer() 

    class Meta:
        model = Post
        fields = ['id', 'owner', 'text', 'created_at']