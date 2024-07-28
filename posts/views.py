from django.shortcuts import render
from rest_framework import generics, status, serializers 
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import User
from accounts.utils import error_detail
from .permissions import IsOwner
from .models import Post
from .serializers import PostSerializer, CreatePostSerializer
from .utils import check_for_obscence
from .filters import PostFilter
from .tasks import create_post
from .pagination import ItemPagination

def auth(request):
    return render(request, template_name='auth.html')

def posts(request):
    return render(request, template_name='posts.html')

def post_details(request, id):
    return render(request, context={'post_id': id}, template_name='post_details.html')

# Create your views here.
class CreatePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    def perform_create(self, serializer):
        post_data = serializer.validated_data
        owner_id = self.request.user.id
        result = create_post.apply_async(args=[owner_id, post_data]).get()
       
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

            

class RetrievePostView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'id'
    

class ListPostView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('created_at')
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter
    pagination_class = ItemPagination
    
    
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