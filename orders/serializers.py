"""
Serializers for orders app.
"""
from rest_framework import serializers
from decimal import Decimal
from .models import Table, Order, OrderItem
from menu.models import MenuItem, Restaurant


# ========== TABLE & QR CODE SERIALIZERS ==========

class TableSerializer(serializers.ModelSerializer):
    """Serializer for Table model with QR code."""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = [
            'id', 'restaurant', 'restaurant_name', 'table_number',
            'qr_code', 'qr_code_image', 'qr_code_url', 'is_active',
            'capacity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'qr_code', 'created_at', 'updated_at']

    def get_qr_code_url(self, obj):
        """Get the full URL for QR code access."""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/v1/customer/qr/{obj.qr_code}/')
        return f'/api/v1/customer/qr/{obj.qr_code}/'


class TableListSerializer(serializers.ModelSerializer):
    """Simplified serializer for table lists."""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    active_orders_count = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = [
            'id', 'table_number', 'restaurant_name', 'qr_code',
            'is_active', 'capacity', 'active_orders_count'
        ]

    def get_active_orders_count(self, obj):
        """Get count of active orders for this table."""
        return obj.orders.filter(
            status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY']
        ).count()


class TableCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tables (restaurant set by viewset)."""
    class Meta:
        model = Table
        fields = ['table_number', 'is_active', 'capacity']


class QRResolveSerializer(serializers.Serializer):
    """Serializer for QR code resolution response."""
    restaurant = serializers.SerializerMethodField()
    table = serializers.SerializerMethodField()
    redirect_url = serializers.SerializerMethodField()

    def get_restaurant(self, obj):
        """Get restaurant information."""
        return {
            'id': obj.restaurant.id,
            'name': obj.restaurant.name,
            'slug': obj.restaurant.slug,
            'logo': obj.restaurant.logo.url if obj.restaurant.logo else None,
            'is_active': obj.restaurant.is_active,
        }

    def get_table(self, obj):
        """Get table information."""
        return {
            'id': obj.id,
            'table_number': obj.table_number,
            'capacity': obj.capacity,
        }

    def get_redirect_url(self, obj):
        """Get the redirect URL for the customer menu."""
        return f'/menu/{obj.restaurant.slug}?table={obj.id}'


# ========== ORDER ITEM SERIALIZERS ==========

class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer for creating order items."""
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    special_instructions = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_menu_item_id(self, value):
        """Validate that menu item exists and is available."""
        try:
            menu_item = MenuItem.objects.get(id=value)
            if not menu_item.is_available:
                raise serializers.ValidationError("This menu item is currently unavailable.")
            return value
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError("Menu item not found.")


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items in responses."""
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_image = serializers.ImageField(source='menu_item.image', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'menu_item', 'menu_item_name', 'menu_item_image',
            'menu_item_snapshot', 'quantity', 'unit_price', 'subtotal',
            'special_instructions', 'created_at'
        ]
        read_only_fields = ['id', 'menu_item_snapshot', 'subtotal', 'created_at']


# ========== ORDER SERIALIZERS ==========

class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders (customer-facing)."""
    restaurant_slug = serializers.SlugField()
    table_id = serializers.IntegerField(required=False, allow_null=True)
    items = OrderItemCreateSerializer(many=True)
    customer_name = serializers.CharField(required=False, allow_blank=True, max_length=100)
    customer_phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    special_instructions = serializers.CharField(required=False, allow_blank=True, max_length=1000)

    def validate_restaurant_slug(self, value):
        """Validate restaurant exists and is active."""
        try:
            restaurant = Restaurant.objects.get(slug=value, is_active=True)
            return value
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("Restaurant not found or not active.")

    def validate_table_id(self, value):
        """Validate table exists and is active."""
        if value:
            try:
                table = Table.objects.get(id=value, is_active=True)
                return value
            except Table.DoesNotExist:
                raise serializers.ValidationError("Table not found or not active.")
        return value

    def validate_items(self, value):
        """Validate that at least one item is in the order."""
        if not value or len(value) == 0:
            raise serializers.ValidationError("Order must contain at least one item.")
        return value

    def validate(self, data):
        """Cross-field validation."""
        # Ensure all items belong to the same restaurant
        restaurant = Restaurant.objects.get(slug=data['restaurant_slug'])
        table_id = data.get('table_id')

        if table_id:
            table = Table.objects.get(id=table_id)
            if table.restaurant != restaurant:
                raise serializers.ValidationError("Table does not belong to this restaurant.")

        # Validate all menu items belong to the restaurant
        item_ids = [item['menu_item_id'] for item in data['items']]
        menu_items = MenuItem.objects.filter(id__in=item_ids).select_related(
            'category__menu_group__restaurant'
        )

        for menu_item in menu_items:
            if menu_item.category.menu_group.restaurant != restaurant:
                raise serializers.ValidationError(
                    f"Menu item '{menu_item.name}' does not belong to this restaurant."
                )

        return data


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for order details."""
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'restaurant', 'restaurant_name',
            'table', 'table_number', 'customer_name', 'customer_phone',
            'status', 'status_display', 'total_amount', 'special_instructions',
            'items', 'created_at', 'confirmed_at', 'prepared_at',
            'ready_at', 'served_at', 'completed_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_at', 'confirmed_at',
            'prepared_at', 'ready_at', 'served_at', 'completed_at', 'updated_at'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for order lists."""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'restaurant_name', 'table_number',
            'customer_name', 'customer_phone', 'status', 'status_display', 'total_amount',
            'items', 'items_count', 'created_at', 'special_instructions'
        ]

    def get_items_count(self, obj):
        """Get total number of items in the order."""
        return obj.items.count()


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status."""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

    def validate_status(self, value):
        """Validate status transition."""
        instance = self.context.get('instance')
        if not instance:
            return value

        # Define valid status transitions
        valid_transitions = {
            'PENDING': ['CONFIRMED', 'CANCELLED'],
            'CONFIRMED': ['PREPARING', 'CANCELLED'],
            'PREPARING': ['READY', 'CANCELLED'],
            'READY': ['SERVED', 'CANCELLED'],
            'SERVED': ['COMPLETED'],
            'COMPLETED': [],
            'CANCELLED': [],
        }

        current_status = instance.status
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {value}."
            )

        return value
