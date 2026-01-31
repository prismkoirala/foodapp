# profiles/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from profiles.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model - includes managed restaurants
    """
    full_name = serializers.SerializerMethodField(read_only=True)
    managed_restaurants = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'phone',
            'email',
            'role',
            'first_name',
            'last_name',
            'full_name',
            'is_active',
            'managed_restaurants',
        ]
        read_only_fields = ['id', 'is_active', 'role']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_managed_restaurants(self, obj):
        """Return list of restaurants this user manages"""
        restaurants = obj.managed_restaurants.all()
        return [
            {
                'id': restaurant.id,
                'name': restaurant.name,
            }
            for restaurant in restaurants
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that:
    1. Accepts phone or email as identifier
    2. Includes user data in response
    3. Only allows MANAGER, OWNER, STAFF roles
    """
    username_field = 'identifier'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop(self.username_field, None)
        self.fields['identifier'] = serializers.CharField(
            required=True,
            help_text="Phone number or email"
        )
        self.fields['password'] = serializers.CharField(
            required=True,
            write_only=True,
            style={'input_type': 'password'}
        )

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['phone'] = user.phone
        token['email'] = user.email
        return token

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')
        
        user = None
        
        # Try email authentication
        if '@' in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass
        else:
            # Try phone authentication
            try:
                user_obj = User.objects.get(phone=identifier)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass
        
        if not user:
            raise serializers.ValidationError(
                _("Unable to log in with provided credentials."),
                code='authorization'
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                _("User account is disabled."),
                code='authorization'
            )
        
        # IMPORTANT: Only allow MANAGER, OWNER, STAFF, COOK, WAITER, CASHIER to login to admin panel
        if user.role not in ['MANAGER', 'OWNER', 'STAFF', 'COOK', 'WAITER', 'CASHIER']:
            raise serializers.ValidationError(
                _("Access denied. Only staff members can access this panel."),
                code='authorization'
            )
        
        # Generate tokens
        refresh = self.get_token(user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        # Add serialized user data to the response
        user_serializer = UserSerializer(user)
        data['user'] = user_serializer.data
        
        return data