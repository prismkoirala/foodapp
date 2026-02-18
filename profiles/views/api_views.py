# profiles/views/api_views.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import logout
from django.http import JsonResponse
from profiles.serializers import CustomTokenObtainPairSerializer, UserSerializer, PromoPhoneNumberSerializer
from profiles.models import PromoPhoneNumber


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    """
    Returns current user data including managed restaurants
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        
        # Use the serializer to format the response
        serializer = UserSerializer(user)
        return Response(serializer.data)


class PromoPhoneNumberCreateView(APIView):
    """
    Public API to create promo phone number entries
    No authentication required - for QR menu users
    """
    def post(self, request):
        try:
            phone_number = request.data.get('phone_number')
            restaurant_id = request.data.get('restaurant_id')
            
            if not phone_number or not restaurant_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Phone number and restaurant ID are required'
                }, status=400)
            
            # Check if this phone number already exists for this restaurant
            existing = PromoPhoneNumber.objects.filter(
                phone_number=phone_number,
                restaurant_id=restaurant_id
            ).first()
            
            if existing:
                return JsonResponse({
                    'success': True,
                    'message': 'Phone number already registered for promos!',
                    'data': {
                        'id': existing.id,
                        'phone_number': existing.phone_number,
                        'created_at': existing.created_at
                    }
                })
            
            # Create new promo phone number entry
            serializer = PromoPhoneNumberSerializer(data={
                'phone_number': phone_number,
                'restaurant': restaurant_id
            })
            
            if serializer.is_valid():
                promo_phone = serializer.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Successfully registered for promos! 🎉',
                    'data': {
                        'id': promo_phone.id,
                        'phone_number': promo_phone.phone_number,
                        'created_at': promo_phone.created_at
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': serializer.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)