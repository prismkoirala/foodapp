"""
URL patterns for manager API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_manager import ManagerMenuItemViewSet, ManagerCategoryViewSet, ManagerRestaurantViewSet

# Create router for viewsets
router = DefaultRouter()
router.register(r'menu-items', ManagerMenuItemViewSet, basename='manager-menuitem')
router.register(r'categories', ManagerCategoryViewSet, basename='manager-category')
router.register(r'restaurant', ManagerRestaurantViewSet, basename='manager-restaurant')

app_name = 'manager'

urlpatterns = [
    path('', include(router.urls)),
]
