from rest_framework import permissions
from django.shortcuts import get_object_or_404
from accounts.models import User

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = get_object_or_404(User, id=request.user.id)
        return obj.owner == user