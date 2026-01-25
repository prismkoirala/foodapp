"""
Manager views for order and table management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta

from ..models import Table, Order, OrderItem
from ..serializers import (
    TableSerializer,
    TableListSerializer,
    TableCreateSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderStatusUpdateSerializer,
)
from ..utils import generate_qr_code_image
from accounts.permissions import IsRestaurantManager


class ManagerTableViewSet(viewsets.ModelViewSet):
    """
    Manager API for table and QR code management.
    """
    queryset = Table.objects.all().select_related('restaurant')
    permission_classes = [IsAuthenticated, IsRestaurantManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['table_number', 'qr_code']
    ordering_fields = ['table_number', 'created_at']
    ordering = ['table_number']

    def get_queryset(self):
        """Filter tables by user's restaurant."""
        queryset = super().get_queryset()
        if self.request.user_role == 'SUPER_ADMIN':
            return queryset
        if self.request.restaurant:
            return queryset.filter(restaurant=self.request.restaurant)
        return queryset.none()

    def get_serializer_class(self):
        """Use different serializers for list, create, and detail."""
        if self.action == 'list':
            return TableListSerializer
        elif self.action == 'create':
            return TableCreateSerializer
        return TableSerializer

    def create(self, request, *args, **kwargs):
        """Create table and return full serializer response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save with restaurant
        if request.user_role != 'SUPER_ADMIN':
            table = serializer.save(restaurant=request.restaurant)
        else:
            table = serializer.save()

        # Generate QR code image if not already generated
        if not table.qr_code_image:
            qr_image = generate_qr_code_image(table.qr_code)
            table.qr_code_image.save(f'qr_{table.qr_code}.png', qr_image, save=True)

        # Return full table details with QR code
        response_serializer = TableSerializer(table, context={'request': request})
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def regenerate_qr(self, request, pk=None):
        """
        Regenerate QR code for a table.
        This invalidates the old QR code.
        """
        table = self.get_object()

        # Generate new QR code
        import secrets
        table.qr_code = secrets.token_urlsafe(16)

        # Generate new QR code image
        qr_image = generate_qr_code_image(table.qr_code)
        table.qr_code_image.save(f'qr_{table.qr_code}.png', qr_image, save=True)
        table.save()

        serializer = self.get_serializer(table)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def qr_code_download(self, request, pk=None):
        """
        Get QR code image for download/printing.
        """
        table = self.get_object()
        if table.qr_code_image:
            return Response({
                'qr_code': table.qr_code,
                'qr_code_image_url': request.build_absolute_uri(table.qr_code_image.url),
                'table_number': table.table_number,
                'restaurant': table.restaurant.name,
            })
        return Response(
            {'detail': 'QR code image not generated yet.'},
            status=status.HTTP_404_NOT_FOUND
        )


class ManagerOrderViewSet(viewsets.ModelViewSet):
    """
    Manager API for order management.
    """
    queryset = Order.objects.all().select_related(
        'restaurant', 'table'
    ).prefetch_related('items__menu_item')
    permission_classes = [IsAuthenticated, IsRestaurantManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'table']
    search_fields = ['order_number', 'customer_name', 'customer_phone']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter orders by user's restaurant."""
        queryset = super().get_queryset()

        if self.request.user_role == 'SUPER_ADMIN':
            return queryset

        if self.request.restaurant:
            queryset = queryset.filter(restaurant=self.request.restaurant)
        else:
            return queryset.none()

        # Additional filtering by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset

    def get_serializer_class(self):
        """Use different serializers for list vs detail."""
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update order status.
        Automatically sets appropriate timestamp fields.
        """
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(
            data=request.data,
            context={'instance': order}
        )

        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            old_status = order.status

            # Update status
            order.status = new_status

            # Set appropriate timestamp
            now = timezone.now()
            if new_status == 'CONFIRMED' and not order.confirmed_at:
                order.confirmed_at = now
            elif new_status == 'PREPARING' and not order.prepared_at:
                order.prepared_at = now
            elif new_status == 'READY' and not order.ready_at:
                order.ready_at = now
            elif new_status == 'SERVED' and not order.served_at:
                order.served_at = now
            elif new_status == 'COMPLETED' and not order.completed_at:
                order.completed_at = now

            order.save()

            response_serializer = OrderSerializer(order, context={'request': request})
            return Response(response_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get order statistics for the restaurant.
        """
        queryset = self.get_queryset()

        # Get date range from query params (default to all time)
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        # Only filter by date if explicitly provided
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        # Calculate statistics
        stats = {
            'total_orders': queryset.count(),
            'pending_orders': queryset.filter(status='PENDING').count(),
            'confirmed_orders': queryset.filter(status='CONFIRMED').count(),
            'preparing_orders': queryset.filter(status='PREPARING').count(),
            'ready_orders': queryset.filter(status='READY').count(),
            'served_orders': queryset.filter(status='SERVED').count(),
            'completed_orders': queryset.filter(status='COMPLETED').count(),
            'cancelled_orders': queryset.filter(status='CANCELLED').count(),
            'total_revenue': queryset.filter(
                status__in=['COMPLETED', 'SERVED']
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'average_order_value': queryset.filter(
                status__in=['COMPLETED', 'SERVED']
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'date_from': str(date_from) if date_from else None,
            'date_to': str(date_to) if date_to else None,
        }

        # Calculate average if there are completed orders
        completed_count = stats['completed_orders'] + stats['served_orders']
        if completed_count > 0:
            stats['average_order_value'] = float(stats['total_revenue']) / completed_count

        return Response(stats)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export orders as CSV.
        """
        # This is a placeholder - you would implement CSV generation here
        return Response({
            'detail': 'CSV export feature coming soon.',
            'suggested_implementation': 'Use django-import-export or custom CSV writer'
        })

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to only allow cancellation, not deletion.
        """
        order = self.get_object()

        if order.status in ['COMPLETED', 'CANCELLED']:
            return Response(
                {'detail': 'Cannot delete completed or cancelled orders.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cancel instead of delete
        order.status = 'CANCELLED'
        order.save()

        return Response(
            {'detail': 'Order cancelled successfully.'},
            status=status.HTTP_200_OK
        )
