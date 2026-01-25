"""
Orders URLs - Customer, Kitchen, and Manager endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import customer_views, kitchen_views, manager_views

# Router for kitchen ViewSet
kitchen_router = DefaultRouter()
kitchen_router.register('orders', kitchen_views.KitchenOrderViewSet, basename='kitchen-order')

# Router for manager ViewSet
manager_router = DefaultRouter()
manager_router.register('orders', manager_views.ManagerOrderViewSet, basename='manager-order')
manager_router.register('tables', manager_views.ManagerTableViewSet, basename='manager-table')

urlpatterns = [
    # Customer order endpoints (public)
    path('qr/<str:qr_code>/', customer_views.qr_resolve_view, name='qr-resolve'),
    path('orders/', customer_views.create_order_view, name='create-order'),
    path('orders/<str:order_number>/', customer_views.order_status_view, name='order-status'),

    # Kitchen endpoints (authenticated)
    path('kitchen/', include(kitchen_router.urls)),

    # Manager endpoints (authenticated)
    path('manager/', include(manager_router.urls)),
]
