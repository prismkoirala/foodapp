# menu/serializers.py
from rest_framework import serializers
from .models import Restaurant, MenuGroup, MenuCategory, MenuItem
from utils.serializers import AnnouncementSerializer


class BulkMenuItemCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating menu items for a specific category
    """
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=50,  # Limit to prevent abuse
        help_text="List of menu items to create"
    )
    
    def validate_items(self, items):
        """Validate each item in the bulk list"""
        required_fields = ['name', 'price']
        optional_fields = ['description', 'item_order', 'is_disabled', 'is_highlight']
        
        for i, item in enumerate(items):
            # Check required fields
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(
                        f"Item {i+1}: Missing required field '{field}'"
                    )
            
            # Validate field types
            if not isinstance(item['name'], str) or not item['name'].strip():
                raise serializers.ValidationError(f"Item {i+1}: Name must be a non-empty string")
            
            try:
                price = float(item['price'])
                if price <= 0:
                    raise serializers.ValidationError(f"Item {i+1}: Price must be greater than 0")
                item['price'] = str(price)  # Convert to string for DecimalField
            except (ValueError, TypeError):
                raise serializers.ValidationError(f"Item {i+1}: Price must be a valid number")
            
            # Validate optional fields
            if 'description' in item and not isinstance(item['description'], str):
                item['description'] = str(item['description'])
            
            if 'item_order' in item:
                try:
                    item_order = int(item['item_order'])
                    if item_order < 0:
                        raise serializers.ValidationError(f"Item {i+1}: Item order must be non-negative")
                    item['item_order'] = item_order
                except (ValueError, TypeError):
                    raise serializers.ValidationError(f"Item {i+1}: Item order must be a valid integer")
            
            if 'is_disabled' in item:
                item['is_disabled'] = bool(item['is_disabled'])
            
            if 'is_highlight' in item:
                item['is_highlight'] = bool(item['is_highlight'])
        
        return items


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
        fields = ('id', 'name', 'image', 'cat_order', 'is_disabled', 'items')
    
    def get_items(self, obj):
        # Include all items (including disabled) - frontend handles disabled state
        all_items = obj.items.all().order_by('item_order')
        return MenuItemSerializer(all_items, many=True).data
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url.replace("/upload/", "/upload/w_400,q_auto,f_auto/")
        return None


class MenuCategoryAdminSerializer(serializers.ModelSerializer):
    """
    Admin serializer for MenuCategory with full CRUD support including image upload.
    """
    image = serializers.SerializerMethodField(read_only=True)
    image_upload = serializers.ImageField(write_only=True, required=False)
    menu_group_name = serializers.CharField(source='menu_group.type', read_only=True)
    item_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = MenuCategory
        fields = (
            'id', 'name', 'image', 'image_upload', 'cat_order', 
            'is_disabled', 'menu_group', 'menu_group_name', 'item_count'
        )
        read_only_fields = ('id',)
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url.replace("/upload/", "/upload/w_400,q_auto,f_auto/")
        return None
    
    def get_item_count(self, obj):
        return obj.items.count()
    
    def create(self, validated_data):
        image_upload = validated_data.pop('image_upload', None)
        category = MenuCategory.objects.create(**validated_data)
        
        if image_upload:
            category.image = image_upload
            category.save()
        
        return category
    
    def update(self, instance, validated_data):
        image_upload = validated_data.pop('image_upload', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if image_upload:
            instance.image = image_upload
        
        instance.save()
        return instance


class MenuGroupSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = MenuGroup
        fields = ('id', 'type', 'group_order', 'categories')


class MenuGroupAdminSerializer(serializers.ModelSerializer):
    """
    Admin serializer for MenuGroup with full CRUD support.
    """
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    category_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = MenuGroup
        fields = (
            'id', 'type', 'group_order', 'restaurant', 'restaurant_name', 'category_count'
        )
        read_only_fields = ('id',)
    
    def get_category_count(self, obj):
        return obj.categories.count()


class RestaurantSerializer(serializers.ModelSerializer):
    menu_groups = MenuGroupSerializer(many=True, read_only=True)
    announcements = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurant
        fields = (
            'id', 'name', 'address', 'phone', 'logo', 'announcements',
            'facebook_url', 'instagram_url', 'tiktok_url', 'menu_groups', 'view_menu_count'
        )
    
    def get_announcements(self, obj):
        # Only return currently active announcements
        active_announcements = obj.announcements.filter(is_active=True)
        return AnnouncementSerializer(active_announcements, many=True).data
    
    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.url.replace("/upload/", "/upload/w_500,q_auto,f_auto/")
        return None