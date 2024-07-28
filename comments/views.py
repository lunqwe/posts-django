from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from posts.pagination import ItemPagination
from posts.permissions import IsOwner
from .models import Comment
from .serializers import CreateCommentSerializer, CommentSerializer
from .filters import CommentFilter
from .tasks import create_comment

class CreateCommentView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CreateCommentSerializer
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    
    def perform_create(self, serializer):
        comment_data = serializer.validated_data
        serialized_comment_data = CommentSerializer(comment_data).data
        owner_id = self.request.user.id
        result = create_comment.apply_async(args=[owner_id, serialized_comment_data]).get()
       
        return result
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if response_data.get('status') == 'success':
            return Response(data=response_data, status=status.HTTP_201_CREATED, headers=headers)    
        else:
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST, headers=headers)

        
class RetrieveCommentView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication, ]
    lookup_field = 'id'
        

class ListCommentView(generics.ListAPIView):
    queryset = Comment.objects.all().order_by('created_at')
    serializer_class =  CommentSerializer
    authentication_classes = [JWTAuthentication, ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CommentFilter
    pagination_class = ItemPagination
    

class UpdateCommentView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication, ]
    permission_classes = (IsAuthenticated, IsOwner)
    lookup_field = 'id'
    
class DeleteCommentView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication, ]
    permission_classes = (IsAuthenticated, IsOwner)
    lookup_field = 'id'
