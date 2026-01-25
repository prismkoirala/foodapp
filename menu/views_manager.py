"""
Manager views for menu item management.
Allows managers to CRUD menu items and mark specials.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import MenuItem, MenuCategory, MenuGroup, Restaurant
from .serializers import MenuItemSerializer, MenuCategorySerializer, RestaurantSerializer
from accounts.permissions import IsRestaurantManager


class MenuItemManagerSerializer(MenuItemSerializer):
    """Extended serializer for manager with writable fields"""
    class Meta(MenuItemSerializer.Meta):
        fields = MenuItemSerializer.Meta.fields + [
            'is_available', 'is_special_of_day', 'preparation_time',
            'allergens', 'dietary_tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ManagerMenuItemViewSet(viewsets.ModelViewSet):
    """
    Manager API for menu item management.
    Managers can create, edit, delete menu items and mark specials.
    """
    queryset = MenuItem.objects.all().select_related(
        'category__menu_group__restaurant'
    )
    serializer_class = MenuItemManagerSerializer
    permission_classes = [IsAuthenticated, IsRestaurantManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available', 'is_special_of_day']
    search_fields = ['name', 'description']
    ordering_fields = ['item_order', 'name', 'price', 'created_at']
    ordering = ['item_order']

    def get_queryset(self):
        """Filter menu items by user's restaurant."""
        queryset = super().get_queryset()

        if self.request.user_role == 'SUPER_ADMIN':
            return queryset

        if self.request.restaurant:
            # Filter by restaurant through category -> menu_group -> restaurant
            queryset = queryset.filter(
                category__menu_group__restaurant=self.request.restaurant
            )
        else:
            return queryset.none()

        return queryset

    def perform_create(self, serializer):
        """
        Validate that the category belongs to manager's restaurant.
        """
        category = serializer.validated_data.get('category')

        if self.request.user_role != 'SUPER_ADMIN':
            if category.menu_group.restaurant != self.request.restaurant:
                raise PermissionError("Cannot create items in other restaurants' categories")

        serializer.save()

    def perform_update(self, serializer):
        """
        Validate that the item belongs to manager's restaurant.
        """
        instance = self.get_object()

        if self.request.user_role != 'SUPER_ADMIN':
            if instance.restaurant != self.request.restaurant:
                raise PermissionError("Cannot update items from other restaurants")

        serializer.save()

    @action(detail=True, methods=['patch'])
    def mark_special(self, request, pk=None):
        """
        Mark/unmark item as today's special.

        PATCH /api/manager/menu-items/{id}/mark_special/
        Body: {"is_special": true/false}
        """
        item = self.get_object()
        is_special = request.data.get('is_special', True)

        item.is_special_of_day = is_special
        item.save()

        serializer = self.get_serializer(item)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def toggle_availability(self, request, pk=None):
        """
        Toggle item availability.

        PATCH /api/manager/menu-items/{id}/toggle_availability/
        Body: {"is_available": true/false}
        """
        item = self.get_object()
        is_available = request.data.get('is_available', not item.is_available)

        item.is_available = is_available
        item.save()

        serializer = self.get_serializer(item)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def specials(self, request):
        """
        Get all items marked as today's special.

        GET /api/manager/menu-items/specials/
        """
        queryset = self.get_queryset().filter(is_special_of_day=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def reorder(self, request):
        """
        Reorder menu items.

        PATCH /api/manager/menu-items/reorder/
        Body: {"items": [{"id": 1, "order": 0}, {"id": 2, "order": 1}, ...]}
        """
        items_data = request.data.get('items', [])

        for item_data in items_data:
            item_id = item_data.get('id')
            new_order = item_data.get('order')

            try:
                item = self.get_queryset().get(id=item_id)
                item.item_order = new_order
                item.save(update_fields=['item_order'])
            except MenuItem.DoesNotExist:
                pass

        return Response({'detail': 'Items reordered successfully'})


class ManagerCategoryViewSet(viewsets.ModelViewSet):
    """
    Manager API for category management.
    """
    queryset = MenuCategory.objects.all().select_related('menu_group__restaurant')
    serializer_class = MenuCategorySerializer
    permission_classes = [IsAuthenticated, IsRestaurantManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['cat_order', 'name']
    ordering = ['cat_order']

    def get_queryset(self):
        """Filter categories by user's restaurant."""
        queryset = super().get_queryset()

        if self.request.user_role == 'SUPER_ADMIN':
            return queryset

        if self.request.restaurant:
            queryset = queryset.filter(menu_group__restaurant=self.request.restaurant)
        else:
            return queryset.none()

        return queryset


class ManagerRestaurantViewSet(viewsets.ModelViewSet):
    """
    Manager API for restaurant settings.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated, IsRestaurantManager]
    http_method_names = ['get', 'patch', 'head', 'options']  # Only allow GET and PATCH

    def get_queryset(self):
        """Only return manager's own restaurant."""
        queryset = super().get_queryset()

        if self.request.user_role == 'SUPER_ADMIN':
            return queryset

        if self.request.restaurant:
            return queryset.filter(id=self.request.restaurant.id)

        return queryset.none()

    def get_object(self):
        """Override to always return the manager's restaurant."""
        if self.request.user_role != 'SUPER_ADMIN':
            return self.request.restaurant
        return super().get_object()
