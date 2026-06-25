from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view, obj=None):
        if obj is not None:
            return self.has_object_permission(request, view, obj)
        return bool(request.user and request.user.is_authenticated)


class CurrentUser(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsAuthor(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

    def has_permission(self, request, view, obj=None):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)
