from rest_framework import permissions

class IsOwnerOrReadonly(permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        """give all users read permission only"""
        if request.method in permissions.SAFE_METHODS:
            return True
        """only object owner can updated or delete"""
        return obj.user == request.user


class IsCartOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """only object owner can view and updated or delete items from their cart"""
        return obj.cart.user == request.user

