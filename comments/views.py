from rest_framework import generics, status, serializers 
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend


from accounts.models import User
from accounts.utils import error_detail
from posts.utils import check_for_obscence
from posts.permissions import IsOwner
from .models import Comment
from .serializers import CreateCommentSerializer, CommentSerializer
from .filters import CommentFilter


class CreateCommentView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CreateCommentSerializer
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                comment_text = serializer.validated_data.get('text')
                if check_for_obscence(comment_text):
                    user = User.objects.get(id=self.request.user.id)
                    serializer.save(owner=user)
                    return Response({'detail': 'Comment created successfully!', 'comment': CommentSerializer(data=serializer.data).initial_data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'detail': 'Your comment is obscene. The comment will not be created.'}, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            data = {
                'status': 'error',
                'detail': error_detail(e)
                }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)   
        
class RetrieveCommentView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication, ]
    lookup_field = 'id'
        

class ListCommentView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class =  CommentSerializer
    authentication_classes = [JWTAuthentication, ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CommentFilter
    

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
