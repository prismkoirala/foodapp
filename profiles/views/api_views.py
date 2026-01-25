from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import logout
from profiles.serializers import LoginSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login endpoint: POST /api/token/
    Body: {"identifier": "phone or email", "password": "..."}
    """
    serializer_class = LoginSerializer

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
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "phone": user.phone,
            "email": user.email,
            "role": user.role,
            "full_name": user.get_full_name(),
            "is_manager_or_owner": user.is_manager_or_owner,
            # add more fields as needed
        }
        return Response(data)