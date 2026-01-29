# menu/serializers.py
from rest_framework import serializers
from .models import Restaurant, MenuGroup, MenuCategory, MenuItem
from utils.serializers import AnnouncementSerializer


class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer for MenuItem with:
    - Read-only optimized image URLs (CloudinaryField transformation)
    - Writable fields for create/update operations
    """
    # For GET requests - return optimized Cloudinary URL
    image = serializers.SerializerMethodField(read_only=True)
    
    # For POST/PUT/PATCH - accept image upload
    image_upload = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = MenuItem
        fields = (
            'id', 'name', 'description', 'price', 'image', 'image_upload',
            'category', 'item_order', 'is_disabled', 'is_highlight'
        )
        read_only_fields = ('id',)
    
    def get_image(self, obj):
        """Return optimized Cloudinary URL for GET requests"""
        if obj.image:
            # Resize to 400px width, auto format, quality 80
            return obj.image.url.replace("/upload/", "/upload/w_400,q_auto,f_auto/")
        return None
    
    def create(self, validated_data):
        """Handle image upload on create"""
        image_upload = validated_data.pop('image_upload', None)
        
        item = MenuItem.objects.create(**validated_data)
        
        if image_upload:
            item.image = image_upload
            item.save()
        
        return item
    
    def update(self, instance, validated_data):
        """Handle image upload on update"""
        image_upload = validated_data.pop('image_upload', None)
        
        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle image upload if provided
        if image_upload:
            instance.image = image_upload
        
        instance.save()
        return instance


class MenuCategorySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuCategory
        fields = ('id', 'name', 'image', 'cat_order', 'items')
    
    def get_items(self, obj):
        # Filter out disabled items + order them
        active_items = obj.items.filter(is_disabled=False).order_by('item_order')
        return MenuItemSerializer(active_items, many=True).data
    
    def get_image(self, obj):
        if obj.image:
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
        fields = (
            'id', 'name', 'address', 'phone', 'logo', 'announcements',
            'facebook_url', 'instagram_url', 'tiktok_url', 'menu_groups'
        )
    
    def get_announcements(self, obj):
        # Only return currently active announcements
        active_announcements = obj.announcements.filter(is_active=True)
        return AnnouncementSerializer(active_announcements, many=True).data
    
    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.url.replace("/upload/", "/upload/w_500,q_auto,f_auto/")
        return None