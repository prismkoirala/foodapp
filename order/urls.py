from django.urls import path

from .api_views import (
    OrderDetail,
    OrderListCreate,
    OrderStatusUpdate,
    RestaurantTableListCreate,
)

urlpatterns = [
    path('tables/', RestaurantTableListCreate.as_view(), name='order-table-list-create'),
    path('orders/', OrderListCreate.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetail.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdate.as_view(), name='order-status-update'),
]
