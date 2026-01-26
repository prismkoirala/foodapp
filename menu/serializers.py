# menu/serializers.py
from rest_framework import serializers
from .models import Restaurant, MenuGroup, MenuCategory, MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description', 'price', 'image', 'item_order')

class MenuCategorySerializer(serializers.ModelSerializer):
    # items = MenuItemSerializer(many=True, read_only=True)
    items = serializers.SerializerMethodField()
    class Meta:
        model = MenuCategory
        fields = ('id', 'name', 'image', 'cat_order', 'items')
    
    def get_items(self, obj):
        # Filter out disabled items + order them
        active_items = obj.items.filter(is_disabled=False).order_by('item_order')
        print('AI->', active_items)
        return MenuItemSerializer(active_items, many=True).data

class MenuGroupSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True, read_only=True)

    class Meta:
        model = MenuGroup
        fields = ('id', 'type', 'group_order', 'categories')

class RestaurantSerializer(serializers.ModelSerializer):
    menu_groups = MenuGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'address', 'phone', 'logo', 'facebook_url', 'instagram_url', 'tiktok_url', 'menu_groups' )