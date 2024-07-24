from django.shortcuts import render
from rest_framework import generics, serializers, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import CreateUserSerializer, LoginUserSerializer, UserSerializer
from .models import User
from .utils import get_user_jwt, error_detail, check_expired_tokens

# registration view
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                data = serializer.validate(data=request.data)
                user = User.objects.create_user(**data)
                user.set_password(data['password'])
                jwt_tokens = get_user_jwt(user)
                return Response({
                        'status': 'success',
                        'detail': "User registered successfully!",
                        'tokens': jwt_tokens
                    })

        except serializers.ValidationError as e:
            data = {
                'status': 'error',
                'detail': error_detail(e)
                }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        

# login view 
class LoginUserView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = LoginUserSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            check_expired_tokens(user)
            jwt_tokens = get_user_jwt(user)
            return Response({
                'status': 'success',
                'detail': "Logged in successfully!",
                'user': {
                        'id': user.id,
                        'tokens': jwt_tokens
                        }
            }, status=status.HTTP_202_ACCEPTED)
        return Response({
            'status': 'error',
            'detail': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
            
            
class UserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def get(self, request, *args, **kwargs):
        try:
            user = self.retrieve(request, *args, **kwargs).data
            if user.get('username') == request.user.username:
                # there could be some user settings, such as notification settings etc.
                return Response({
                            'status': 'success',
                            'data_type': "private",
                            "user": user,
                        }, status=status.HTTP_200_OK)
            # some public data (e.g. username, date joined)
            else:
                return Response({
                    'status': 'success',
                    'deta_type': "public",
                    "user": user.get('username'),
                })

        except serializers.ValidationError as e:
            data = {
                'status': 'error',
                'detail': error_detail(e)
                }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
