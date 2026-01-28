# menu/serializers.py
from rest_framework import serializers
from .models import Restaurant, MenuGroup, MenuCategory, MenuItem
from utils.serializers import AnnouncementSerializer
class MenuItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description', 'price', 'image', 'item_order')

    def get_image(self, obj):
        if obj.image:
            # example: resize to 400px width, auto format, quality 80
            return obj.image.url.replace("/upload/", "/upload/w_400,q_auto,f_auto/")
        return None

class MenuCategorySerializer(serializers.ModelSerializer):
    # items = MenuItemSerializer(many=True, read_only=True)
    items = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = MenuCategory
        fields = ('id', 'name', 'image', 'cat_order', 'items')
    
    def get_items(self, obj):
        # Filter out disabled items + order them
        active_items = obj.items.filter(is_disabled=False).order_by('item_order')
        print('AI->', active_items)
        return MenuItemSerializer(active_items, many=True).data
    
    def get_image(self, obj):
        if obj.image:
            # example: resize to 400px width, auto format, quality 80
            return obj.image.url.replace("/upload/", "/upload/w_400,q_auto,f_auto/")
        return None

class MenuGroupSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True, read_only=True)

    class Meta:
        model = MenuGroup
        fields = ('id', 'type', 'group_order', 'categories')

class RestaurantSerializer(serializers.ModelSerializer):
    menu_groups = MenuGroupSerializer(many=True, read_only=True)
    announcements = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'address', 'phone', 'logo', 'announcements', 'facebook_url', 'instagram_url', 'tiktok_url', 'menu_groups' )
        
    def get_announcements(self, obj):
        # Only return currently active announcements
        active_announcements = obj.announcements.filter(is_active=True)
        return AnnouncementSerializer(active_announcements, many=True).data

    def get_logo(self, obj):
        if obj.logo:
            # example: resize to 400px width, auto format, quality 80
            return obj.logo.url.replace("/upload/", "/upload/w_500,q_auto,f_auto/")
        return None
