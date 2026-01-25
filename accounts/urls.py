"""
URL patterns for accounts app.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User profile endpoints
    path('me/', views.current_user_view, name='current_user'),
    path('profile/', views.update_profile_view, name='update_profile'),
]
