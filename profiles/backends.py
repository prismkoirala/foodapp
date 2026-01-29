# profiles/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class PhoneOrEmailBackend(ModelBackend):
    """
    Custom authentication backend that allows login with phone or email
    """
    def authenticate(self, request, username=None, password=None, phone=None, email=None, **kwargs):
        try:
            # Try to find user by phone
            if phone or (username and '@' not in username):
                identifier = phone or username
                user = User.objects.get(phone=identifier)
            # Try to find user by email
            elif email or (username and '@' in username):
                identifier = email or username
                user = User.objects.get(email=identifier)
            else:
                return None
                
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None
        
        return None