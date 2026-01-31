# menu/views/api_views.py
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from menu.models import Restaurant, MenuGroup, MenuCategory, MenuItem
from menu.serializers import (
    RestaurantSerializer, MenuGroupSerializer,
    MenuCategorySerializer, MenuCategoryAdminSerializer, MenuItemSerializer
)


# ============================================
# ORIGINAL VIEWS - For Customer QR Menu
# (Keep these exactly as they were)
# ============================================

class RestaurantDetail(generics.RetrieveAPIView):
    """Public view - Get restaurant details for QR menu"""
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'menu_groups__categories__items'
        )


class MenuGroupList(generics.ListAPIView):
    """Public view - List menu groups for customer"""
    queryset = MenuGroup.objects.all()
    serializer_class = MenuGroupSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant', None)
        if restaurant_id is not None:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        return queryset


class MenuCategoryList(generics.ListAPIView):
    """Public view - List categories for customer"""
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        menu_group_id = self.request.query_params.get('menu_group', None)
        if menu_group_id is not None:
            queryset = queryset.filter(menu_group_id=menu_group_id)
        return queryset


class MenuItemList(generics.ListAPIView):
    """Public view - List menu items for customer"""
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class HighlightedMenuItemsList(generics.ListAPIView):
    """Public view - List highlighted items for customer"""
    serializer_class = MenuItemSerializer
    
    def get_queryset(self):
        return MenuItem.objects.filter(
            category__menu_group__restaurant__pk=self.kwargs['restaurant_pk'],
            is_highlight=True,
            is_disabled=False
        ).order_by('item_order')


# ============================================
# NEW ADMIN VIEWS - For Restaurant Management
# (These require authentication and filter by user's restaurant)
# ============================================

class RestaurantDetailAdmin(generics.RetrieveAPIView):
    """Admin view - Get restaurant details for manager"""
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        user = self.request.user
        return Restaurant.objects.filter(
            managers_and_staff=user
        ).prefetch_related('menu_groups__categories__items')


class MenuGroupListAdmin(generics.ListAPIView):
    """Admin view - List menu groups for manager's restaurant"""
    queryset = MenuGroup.objects.all()
    serializer_class = MenuGroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = MenuGroup.objects.filter(
            restaurant__managers_and_staff=user
        )
        
        restaurant_id = self.request.query_params.get('restaurant', None)
        if restaurant_id is not None:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        
        return queryset


class MenuCategoryListAdmin(generics.ListCreateAPIView):
    """
    Admin view - List and create categories
    GET: List categories (only from manager's restaurant)
    POST: Create a new category (only in manager's restaurant)
    """
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategoryAdminSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = MenuCategory.objects.filter(
            menu_group__restaurant__managers_and_staff=user
        )
        
        menu_group_id = self.request.query_params.get('menu_group', None)
        if menu_group_id is not None:
            queryset = queryset.filter(menu_group_id=menu_group_id)
        
        # Filter by is_disabled if provided
        is_disabled = self.request.query_params.get('is_disabled', None)
        if is_disabled is not None:
            queryset = queryset.filter(is_disabled=is_disabled.lower() == 'true')
        
        return queryset.order_by('cat_order', 'id')
    
    def perform_create(self, serializer):
        """Ensure user can only create categories in menu groups they manage"""
        menu_group = serializer.validated_data.get('menu_group')
        user = self.request.user
        
        if not menu_group.restaurant.managers_and_staff.filter(id=user.id).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to add categories to this menu group.")
        
        serializer.save()


class MenuCategoryDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin view - Manage single category
    GET/PUT/PATCH/DELETE: Only from manager's restaurant
    """
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategoryAdminSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        user = self.request.user
        return MenuCategory.objects.filter(
            menu_group__restaurant__managers_and_staff=user
        )
    
    def perform_update(self, serializer):
        """Ensure user can only update categories they manage"""
        instance = self.get_object()
        user = self.request.user
        
        if not instance.menu_group.restaurant.managers_and_staff.filter(id=user.id).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to update this category.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure user can only delete categories they manage"""
        user = self.request.user
        
        if not instance.menu_group.restaurant.managers_and_staff.filter(id=user.id).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to delete this category.")
        
        instance.delete()


class MenuItemListAdmin(generics.ListCreateAPIView):
    """
    Admin view - List and create menu items
    GET: List menu items (only from manager's restaurant)
    POST: Create a new menu item (only in manager's restaurant)
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        user = self.request.user
        
        # CRITICAL: Only return items from restaurants this user manages
        queryset = MenuItem.objects.filter(
            category__menu_group__restaurant__managers_and_staff=user
        )
        
        # Filter by category if provided
        category_id = self.request.query_params.get('category', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by is_disabled if provided
        is_disabled = self.request.query_params.get('is_disabled', None)
        if is_disabled is not None:
            queryset = queryset.filter(is_disabled=is_disabled.lower() == 'true')
        
        # Filter by is_highlight if provided
        is_highlight = self.request.query_params.get('is_highlight', None)
        if is_highlight is not None:
            queryset = queryset.filter(is_highlight=is_highlight.lower() == 'true')
        
        return queryset.order_by('item_order', 'id')
    
    def perform_create(self, serializer):
        """Ensure user can only create items in categories they manage"""
        category = serializer.validated_data.get('category')
        user = self.request.user
        
        # Verify the category belongs to a restaurant this user manages
        if not category.menu_group.restaurant.managers_and_staff.filter(id=user.id).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to add items to this category.")
        
        serializer.save()


class MenuItemDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin view - Manage single menu item
    GET/PUT/PATCH/DELETE: Only from manager's restaurant
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        user = self.request.user
        # Only return items from restaurants this user manages
        return MenuItem.objects.filter(
            category__menu_group__restaurant__managers_and_staff=user
        )
    
    def perform_update(self, serializer):
        """Ensure user can only update items they manage"""
        instance = self.get_object()
        user = self.request.user
        
        # Verify the item belongs to a restaurant this user manages
        if not instance.category.menu_group.restaurant.managers_and_staff.filter(id=user.id).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to update this item.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure user can only delete items they manage"""
        user = self.request.user
        
        # Verify the item belongs to a restaurant this user manages
        if not instance.category.menu_group.restaurant.managers_and_staff.filter(id=user.id).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to delete this item.")
        
        instance.delete()


class HighlightedMenuItemsListAdmin(generics.ListAPIView):
    """Admin view - List highlighted items for manager's restaurant"""
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        restaurant_pk = self.kwargs['restaurant_pk']
        
        # Verify user manages this restaurant
        return MenuItem.objects.filter(
            category__menu_group__restaurant__pk=restaurant_pk,
            category__menu_group__restaurant__managers_and_staff=user,
            is_highlight=True,
            is_disabled=False
        ).order_by('item_order')