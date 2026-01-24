# menu/serializers.py
from rest_framework import serializers
from .models import Restaurant, MenuGroup, MenuCategory, MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description', 'price', 'image', 'item_order')

class MenuCategorySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = ('id', 'name', 'image', 'cat_order', 'items')

class MenuGroupSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True, read_only=True)

    class Meta:
        model = MenuGroup
        fields = ('id', 'type', 'group_order', 'categories')

class RestaurantSerializer(serializers.ModelSerializer):
    menu_groups = MenuGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'address', 'phone', 'logo', 'menu_groups')