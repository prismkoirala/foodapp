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


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'menu_item', 'menu_item_name', 'quantity', 'unit_price')
        read_only_fields = ('id', 'unit_price')


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

        if table is None:
            raise serializers.ValidationError({'table': 'This field is required.'})

        if not table.is_active:
            raise serializers.ValidationError({'table': 'Table is not active.'})

        if table and table.restaurant_id != restaurant.id:
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
        return order

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)
