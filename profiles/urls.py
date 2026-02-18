from django.urls import path
from profiles.views.api_views import (
    CustomTokenObtainPairView,
    LogoutView,
    CurrentUserView,
    PromoPhoneNumberCreateView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),   # login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('promo-phone-number/', PromoPhoneNumberCreateView.as_view(), name='promo-phone-number'),
]