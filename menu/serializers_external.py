"""
Serializers matching the external API format from gipech.pythonanywhere.com
"""
from rest_framework import serializers
from .models import Restaurant, MenuGroup, MenuCategory, MenuItem


class ExternalMenuItemSerializer(serializers.ModelSerializer):
    """Menu item serializer for external API format"""
    id = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(source='item_order', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'order', 'description']


class ExternalMenuCategorySerializer(serializers.ModelSerializer):
    """Menu category serializer for external API format"""
    id = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(source='cat_order', read_only=True)
    items = ExternalMenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'order', 'items']


class ExternalMenuGroupSerializer(serializers.ModelSerializer):
    """Menu group serializer for external API format"""
    id = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(source='group_order', read_only=True)
    categories = ExternalMenuCategorySerializer(many=True, read_only=True)

    class Meta:
        model = MenuGroup
        fields = ['id', 'type', 'order', 'categories']


class ExternalRestaurantSerializer(serializers.ModelSerializer):
    """Restaurant serializer for external API format"""
    id = serializers.IntegerField(read_only=True)
    menu_groups = ExternalMenuGroupSerializer(many=True, read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'phone', 'logo', 'menu_groups']

    def get_logo(self, obj):
        """Return full URL for logo if it exists"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
