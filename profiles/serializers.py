from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

class LoginSerializer(serializers.Serializer):
    """
    Custom login: phone + password OR email + password
    """
    identifier = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Phone number or email"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        if '@' in identifier:  # treat as email
            user = authenticate(
                request=self.context.get('request'),
                email=identifier,
                password=password
            )
        else:  # treat as phone
            user = authenticate(
                request=self.context.get('request'),
                phone=identifier,
                password=password
            )

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

        attrs['user'] = user
        return attrs