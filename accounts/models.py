from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status

class UserManager(BaseUserManager):
    
    def create_user(self, email: str, username: str, password: str=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set.')
        
        normalized_email = self.normalize_email(email=email)
        user = self.model(email=normalized_email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    
    def create_superuser(self, email: str, username: str, password: str, **extra_fields):
        extra_fields.setdefault(is_staff=True)
        extra_fields.setdefault(is_superuser=True)
        
        return User.objects.create_user(email=email, username=username, password=password, **extra_fields)
        

class User(AbstractUser):
    username = models.CharField("Username", max_length=255, unique=True)
    email = models.EmailField('Email', unique=True)