from django.urls import path

from .api_views import (
    OrderDetail,
    OrderListCreate,
    OrderStatusUpdate,
    RestaurantTableListCreate,
    # Admin views
    RestaurantTableListAdmin,
    RestaurantTableDetailAdmin,
    OrderListAdmin,
    OrderDetailAdmin,
    # Item management
    OrderItemStatusUpdateView,
    OrderAddItemView,
    OrderCheckoutView,
)

urlpatterns = [
    # Public/existing endpoints
    path('tables/', RestaurantTableListCreate.as_view(), name='order-table-list-create'),
    path('orders/', OrderListCreate.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetail.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdate.as_view(), name='order-status-update'),

    # Admin endpoints - Tables (Manager/Owner only)
    path('admin/tables/', RestaurantTableListAdmin.as_view(), name='admin-table-list'),
    path('admin/tables/<int:pk>/', RestaurantTableDetailAdmin.as_view(), name='admin-table-detail'),

    # Admin endpoints - Orders (Waiter/Cashier/Manager/Owner)
    path('admin/orders/', OrderListAdmin.as_view(), name='admin-order-list'),
    path('admin/orders/<int:pk>/', OrderDetailAdmin.as_view(), name='admin-order-detail'),
    
    # Item management endpoints
    path('admin/orders/<int:order_id>/items/', OrderAddItemView.as_view(), name='order-add-item'),
    path('admin/items/<int:pk>/status/', OrderItemStatusUpdateView.as_view(), name='order-item-status-update'),
    
    # Checkout endpoint
    path('admin/orders/<int:pk>/checkout/', OrderCheckoutView.as_view(), name='order-checkout'),
]
