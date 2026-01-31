from django.db import transaction
from rest_framework import serializers

from menu.models import MenuItem, Restaurant
from .models import Order, OrderItem, RestaurantTable


class RestaurantTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantTable
        fields = ('id', 'restaurant', 'name', 'capacity', 'is_active')
        read_only_fields = ('id',)


class OrderItemCreateSerializer(serializers.Serializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class OrderItemStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('status',)
        
    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in OrderItem.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'menu_item', 'menu_item_name', 'quantity', 'unit_price', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'unit_price', 'created_at', 'updated_at')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'restaurant', 'table', 'status', 'created_by',
            'created_at', 'updated_at', 'items', 'total'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at', 'items', 'total')

    def get_total(self, obj):
        return str(obj.total)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ('id', 'restaurant', 'table', 'status', 'items')
        read_only_fields = ('id', 'status')

    def validate(self, attrs):
        restaurant = attrs.get('restaurant') or self.context.get('restaurant')
        table = attrs.get('table')
        items = attrs.get('items')

        if restaurant is None:
            raise serializers.ValidationError({'restaurant': 'This field is required.'})

        # Table is optional - validate only if provided
        if table is not None:
            if not table.is_active:
                raise serializers.ValidationError({'table': 'Table is not active.'})

            if table.restaurant_id != restaurant.id:
                raise serializers.ValidationError({'table': 'Table does not belong to this restaurant.'})

        if not items:
            raise serializers.ValidationError({'items': 'At least one item is required.'})

        seen_menu_item_ids = set()
        for item in items:
            menu_item = item['menu_item']

            if menu_item.id in seen_menu_item_ids:
                raise serializers.ValidationError({'items': f'Menu item {menu_item.id} is duplicated in the request.'})
            seen_menu_item_ids.add(menu_item.id)

            if menu_item.is_disabled:
                raise serializers.ValidationError({'items': f'Menu item {menu_item.id} is disabled.'})
            if menu_item.category.menu_group.restaurant_id != restaurant.id:
                raise serializers.ValidationError({'items': f'Menu item {menu_item.id} does not belong to this restaurant.'})

        attrs['restaurant'] = restaurant
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')

        created_by = None
        if request and request.user and request.user.is_authenticated:
            created_by = request.user

        order = Order.objects.create(created_by=created_by, **validated_data)

        order_items = []
        for item in items_data:
            menu_item = item['menu_item']
            quantity = item['quantity']
            order_items.append(
                OrderItem(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    unit_price=menu_item.price,
                )
            )

        OrderItem.objects.bulk_create(order_items)
        
        # Refresh instance to get items with prefetch
        order = Order.objects.select_related(
            'restaurant', 'table', 'created_by'
        ).prefetch_related(
            'items__menu_item'
        ).get(pk=order.pk)
        
        return order

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)


# ────────────────────────────────────────────────
# Admin Serializers
# ────────────────────────────────────────────────

class RestaurantTableAdminSerializer(serializers.ModelSerializer):
    """
    Admin serializer for RestaurantTable with full CRUD support.
    """
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    order_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RestaurantTable
        fields = (
            'id', 'name', 'capacity', 'is_active', 'restaurant', 'restaurant_name', 'order_count'
        )
        read_only_fields = ('id',)

    def get_order_count(self, obj):
        return obj.orders.count()


class OrderAdminSerializer(serializers.ModelSerializer):
    """
    Admin serializer for Order with full CRUD support.
    Includes Nepali date fields for day book / filtering.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    table_name = serializers.CharField(source='table.name', read_only=True, allow_null=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    nepali_date_formatted = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'restaurant', 'restaurant_name', 'table', 'table_name',
            'status', 'created_by', 'created_by_name', 'created_at', 'updated_at',
            'nepali_date', 'nepali_year', 'nepali_month', 'nepali_day', 'nepali_date_formatted',
            'items', 'total', 'final_total'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'nepali_date', 'nepali_year', 'nepali_month', 'nepali_day')

    def get_total(self, obj):
        return str(obj.total)

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.phone or obj.created_by.email
        return None


class OrderCheckoutSerializer(serializers.ModelSerializer):
    """
    Serializer for completing checkout with final_total.
    """
    class Meta:
        model = Order
        fields = ('final_total',)
