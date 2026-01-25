"""
Serializers for accounts app.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import RestaurantUser
from menu.models import Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    """
    Serializer for Restaurant model (basic info for user profile).
    """
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug', 'logo']
        read_only_fields = ['id', 'slug']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django User model.
    """
    restaurant = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'restaurant', 'role', 'phone_number']
        read_only_fields = ['id', 'username']

    def get_restaurant(self, obj):
        """Get restaurant information for the user."""
        try:
            restaurant_user = obj.restaurant_user
            if restaurant_user.restaurant:
                return RestaurantSerializer(restaurant_user.restaurant).data
            return None
        except RestaurantUser.DoesNotExist:
            return None

    def get_role(self, obj):
        """Get user role."""
        try:
            return obj.restaurant_user.role
        except RestaurantUser.DoesNotExist:
            return None

    def get_phone_number(self, obj):
        """Get user phone number."""
        try:
            return obj.restaurant_user.phone_number
        except RestaurantUser.DoesNotExist:
            return None


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        """
        Validate user credentials.
        """
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')

                # Check if user has a RestaurantUser profile
                try:
                    restaurant_user = user.restaurant_user
                    if not restaurant_user.is_active:
                        raise serializers.ValidationError('User account is not active.')
                except RestaurantUser.DoesNotExist:
                    # User exists but has no restaurant profile
                    # This might be a superuser created via createsuperuser
                    if not user.is_superuser:
                        raise serializers.ValidationError('User is not authorized to access this system.')

                data['user'] = user
                return data
            else:
                raise serializers.ValidationError('Invalid username or password.')
        else:
            raise serializers.ValidationError('Must include username and password.')


class RestaurantUserSerializer(serializers.ModelSerializer):
    """
    Serializer for RestaurantUser model.
    """
    user = UserSerializer(read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = RestaurantUser
        fields = ['id', 'user', 'restaurant', 'restaurant_name', 'role', 'phone_number', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
