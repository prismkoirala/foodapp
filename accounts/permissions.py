"""
Custom permission classes for multi-tenancy and role-based access control.
"""
from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission class to check if user is a super admin.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request, 'user_role') and
            request.user_role == 'SUPER_ADMIN'
        )


class IsRestaurantManager(permissions.BasePermission):
    """
    Permission class to check if user is a restaurant manager or super admin.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Set restaurant context if not already set (for JWT auth)
        if not hasattr(request, 'user_role') or request.user_role is None:
            try:
                restaurant_user = request.user.restaurant_user
                request.restaurant = restaurant_user.restaurant
                request.user_role = restaurant_user.role
            except (AttributeError, RestaurantUser.DoesNotExist):
                return False

        return request.user_role in ['SUPER_ADMIN', 'RESTAURANT_MANAGER']

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission to ensure user can only manage their own restaurant's data.
        """
        if request.user_role == 'SUPER_ADMIN':
            return True

        # Check if object has a restaurant attribute
        if hasattr(obj, 'restaurant'):
            return obj.restaurant == request.restaurant

        # If the object is a Restaurant itself
        if obj.__class__.__name__ == 'Restaurant':
            return obj == request.restaurant

        return False


class IsKitchenStaff(permissions.BasePermission):
    """
    Permission class for kitchen staff (includes managers and super admins).
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Set restaurant context if not already set (for JWT auth)
        if not hasattr(request, 'user_role') or request.user_role is None:
            try:
                from .models import RestaurantUser
                restaurant_user = request.user.restaurant_user
                request.restaurant = restaurant_user.restaurant
                request.user_role = restaurant_user.role
            except (AttributeError, RestaurantUser.DoesNotExist):
                return False

        return request.user_role in ['SUPER_ADMIN', 'RESTAURANT_MANAGER', 'KITCHEN_STAFF']

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for kitchen staff.
        """
        if request.user_role == 'SUPER_ADMIN':
            return True

        # Check if object has a restaurant attribute
        if hasattr(obj, 'restaurant'):
            return obj.restaurant == request.restaurant

        return False


class IsRestaurantOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of a restaurant to access it.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user_role == 'SUPER_ADMIN':
            return True

        # For Restaurant objects
        if obj.__class__.__name__ == 'Restaurant':
            return obj == request.restaurant

        # For objects with a restaurant foreign key
        if hasattr(obj, 'restaurant'):
            return obj.restaurant == request.restaurant

        # For MenuItem (restaurant is accessed through category.menu_group.restaurant)
        if obj.__class__.__name__ == 'MenuItem':
            return obj.category.menu_group.restaurant == request.restaurant

        return False


class AllowAnonymousRead(permissions.BasePermission):
    """
    Permission class that allows anonymous users to read (GET)
    but requires authentication for other methods.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require authentication for other methods
        return request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the owner's restaurant
        if request.user_role == 'SUPER_ADMIN':
            return True

        if hasattr(obj, 'restaurant'):
            return obj.restaurant == request.restaurant

        return False
