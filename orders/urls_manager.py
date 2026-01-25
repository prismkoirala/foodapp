"""
URL patterns for manager order and table management API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.manager_views import ManagerTableViewSet, ManagerOrderViewSet

# Create router for viewsets
router = DefaultRouter()
router.register(r'tables', ManagerTableViewSet, basename='manager-table')
router.register(r'orders', ManagerOrderViewSet, basename='manager-order')

app_name = 'manager_orders'

urlpatterns = [
    path('', include(router.urls)),
]
