"""
Customer-facing views for orders.
Includes QR code resolution and order creation (no authentication required).
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from ..models import Table, Order, OrderItem
from ..serializers import (
    QRResolveSerializer,
    OrderCreateSerializer,
    OrderSerializer,
)
from menu.models import MenuItem, Restaurant


@api_view(['GET'])
@permission_classes([AllowAny])
def qr_resolve_view(request, qr_code):
    """
    Resolve a QR code to restaurant and table information.
    Returns data needed to redirect customer to menu.

    GET /api/v1/customer/qr/{qr_code}/
    """
    table = get_object_or_404(Table, qr_code=qr_code, is_active=True)

    # Check if restaurant is active
    if not table.restaurant.is_active:
        return Response(
            {'detail': 'This restaurant is currently not accepting orders.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    serializer = QRResolveSerializer(table, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_order_view(request):
    """
    Create a new order (customer-facing, no authentication required).

    POST /api/v1/customer/orders/

    Request body:
    {
        "restaurant_slug": "joes-pizza",
        "table_id": 5,  // optional
        "items": [
            {
                "menu_item_id": 10,
                "quantity": 2,
                "special_instructions": "No onions"
            }
        ],
        "customer_name": "John Doe",  // optional
        "customer_phone": "+1-555-0100",  // optional
        "special_instructions": "Extra napkins"  // optional
    }
    """
    serializer = OrderCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create order with transaction
    try:
        with transaction.atomic():
            data = serializer.validated_data

            # Get restaurant and table
            restaurant = Restaurant.objects.get(slug=data['restaurant_slug'])
            table = None
            if data.get('table_id'):
                table = Table.objects.get(id=data['table_id'])

            # Create order
            order = Order.objects.create(
                restaurant=restaurant,
                table=table,
                customer_name=data.get('customer_name', ''),
                customer_phone=data.get('customer_phone', ''),
                special_instructions=data.get('special_instructions', ''),
                total_amount=Decimal('0.00'),  # Will be calculated
                status='PENDING'
            )

            # Create order items and calculate total
            total_amount = Decimal('0.00')
            item_ids = [item['menu_item_id'] for item in data['items']]
            menu_items = {
                mi.id: mi for mi in MenuItem.objects.filter(id__in=item_ids)
            }

            for item_data in data['items']:
                menu_item = menu_items[item_data['menu_item_id']]
                quantity = item_data['quantity']
                unit_price = menu_item.price
                subtotal = quantity * unit_price

                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal,
                    special_instructions=item_data.get('special_instructions', ''),
                    menu_item_snapshot={
                        'name': menu_item.name,
                        'description': menu_item.description,
                        'price': str(menu_item.price),
                        'category': menu_item.category.name,
                        'preparation_time': menu_item.preparation_time,
                    }
                )

                total_amount += subtotal

            # Update order total
            order.total_amount = total_amount
            order.save()

            # Return created order
            response_serializer = OrderSerializer(order, context={'request': request})
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

    except Exception as e:
        return Response(
            {'detail': f'Error creating order: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def order_status_view(request, order_number):
    """
    Get order status by order number (for customer tracking).

    GET /api/v1/customer/orders/{order_number}/
    """
    order = get_object_or_404(Order, order_number=order_number)
    serializer = OrderSerializer(order, context={'request': request})
    return Response(serializer.data)
