"""
URL patterns for customer-facing order API.
"""
from django.urls import path
from .views.customer_views import (
    qr_resolve_view,
    create_order_view,
    order_status_view,
)

app_name = 'customer_orders'

urlpatterns = [
    # QR Code resolution
    path('qr/<str:qr_code>/', qr_resolve_view, name='qr-resolve'),

    # Order creation and tracking
    path('orders/', create_order_view, name='create-order'),
    path('orders/<str:order_number>/', order_status_view, name='order-status'),
]
