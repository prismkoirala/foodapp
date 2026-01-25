"""
Menu serializers matching external API format
"""
from rest_framework import serializers
from .models import Restaurant, MenuGroup, MenuCategory, MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    """Menu item serializer"""
    id = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(source='item_order', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'order', 'description', 'image']

    def get_image(self, obj):
        """Return full URL for image if it exists"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class MenuCategorySerializer(serializers.ModelSerializer):
    """Menu category serializer"""
    id = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(source='cat_order', read_only=True)
    items = MenuItemSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'order', 'items', 'image']

    def get_image(self, obj):
        """Return full URL for image if it exists"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class MenuGroupSerializer(serializers.ModelSerializer):
    """Menu group serializer"""
    id = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(source='group_order', read_only=True)
    categories = MenuCategorySerializer(many=True, read_only=True)

    class Meta:
        model = MenuGroup
        fields = ['id', 'type', 'order', 'categories']


class RestaurantSerializer(serializers.ModelSerializer):
    """Restaurant serializer with full menu"""
    id = serializers.IntegerField(read_only=True)
    menu_groups = MenuGroupSerializer(many=True, read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug', 'address', 'phone', 'logo', 'menu_groups']

    def get_logo(self, obj):
        """Return full URL for logo if it exists"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class RestaurantListSerializer(serializers.ModelSerializer):
    """Simple restaurant list serializer"""
    id = serializers.IntegerField(read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug', 'address', 'phone', 'logo']

    def get_logo(self, obj):
        """Return full URL for logo if it exists"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
