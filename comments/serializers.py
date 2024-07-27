from rest_framework import serializers 

from .models import Comment

class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['owner', 'post', 'text']
        
        
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'owner', 'post', 'text', 'created_at']
        
