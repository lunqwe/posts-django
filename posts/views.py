from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import User
from .permissions import IsOwner
from .models import Post
from .serializers import PostSerializer
from .utils import check_for_obscence
from .filters import PostFilter

# Create your views here.
class CreatePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            post_text = serializer.validated_data.get('text')
            if check_for_obscence(post_text):
                user = User.objects.get(id=self.request.user.id)
                serializer.save(owner=user)
                return Response({'detail': 'Post created successfully!', 'post': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': "Your post is obscene. The post will not be created."}, status=status.HTTP_400_BAD_REQUEST)
            

class RetrievePostView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'id'
    

class ListPostView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter
    
    
class UpdatePostView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]
    lookup_field = 'id'
    
class DeletePostView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]
    lookup_field = 'id'