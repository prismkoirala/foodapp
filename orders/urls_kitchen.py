"""
URL patterns for kitchen display API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.kitchen_views import KitchenOrderViewSet

# Create router for viewsets
router = DefaultRouter()
router.register(r'orders', KitchenOrderViewSet, basename='kitchen-order')

app_name = 'kitchen'

urlpatterns = [
    path('', include(router.urls)),
]
