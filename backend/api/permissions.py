from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user

    def has_permission(self, request, view, obj=None):
        if obj is not None:
            return self.has_object_permission(request, view, obj)
        return request.user and request.user.is_authenticated

class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

    def has_permission(self, request, view, obj=None):
        if obj is not None:
            return self.has_object_permission(request, view, obj)
        return request.user and request.user.is_authenticated

class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

    def has_permission(self, request, view, obj=None):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated