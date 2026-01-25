"""
Kitchen staff views for order display and management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Q

from ..models import Order
from ..serializers import OrderSerializer, OrderListSerializer, OrderStatusUpdateSerializer
from accounts.permissions import IsKitchenStaff


class KitchenOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Kitchen API for viewing and updating orders.
    Kitchen staff can view orders and update their status.
    """
    queryset = Order.objects.all().select_related(
        'restaurant', 'table'
    ).prefetch_related('items__menu_item')
    permission_classes = [IsAuthenticated, IsKitchenStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'table']
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        """
        Filter orders by user's restaurant and show only active orders.
        """
        queryset = super().get_queryset()

        if self.request.user_role == 'SUPER_ADMIN':
            return queryset

        if self.request.restaurant:
            queryset = queryset.filter(restaurant=self.request.restaurant)
        else:
            return queryset.none()

        # By default, only show active orders (not completed or cancelled)
        show_all = self.request.query_params.get('show_all', 'false').lower() == 'true'
        if not show_all:
            queryset = queryset.filter(
                status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY']
            )

        return queryset

    def get_serializer_class(self):
        """Use different serializers for list vs detail."""
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update order status from kitchen.
        Kitchen staff can move orders through preparation stages.
        """
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(
            data=request.data,
            context={'instance': order}
        )

        if serializer.is_valid():
            new_status = serializer.validated_data['status']

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

            order.save()

            response_serializer = OrderSerializer(order, context={'request': request})
            return Response(response_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def pending_count(self, request):
        """
        Get count of pending orders.
        Useful for real-time notifications.
        """
        queryset = self.get_queryset()
        counts = {
            'pending': queryset.filter(status='PENDING').count(),
            'confirmed': queryset.filter(status='CONFIRMED').count(),
            'preparing': queryset.filter(status='PREPARING').count(),
            'ready': queryset.filter(status='READY').count(),
            'total_active': queryset.filter(
                status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY']
            ).count(),
        }
        return Response(counts)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get orders grouped by status (for Kanban board).
        Returns orders in four columns: PENDING, CONFIRMED, PREPARING, READY.
        """
        queryset = self.get_queryset()

        pending_orders = queryset.filter(status='PENDING')
        confirmed_orders = queryset.filter(status='CONFIRMED')
        preparing_orders = queryset.filter(status='PREPARING')
        ready_orders = queryset.filter(status='READY')

        return Response({
            'PENDING': OrderListSerializer(
                pending_orders,
                many=True,
                context={'request': request}
            ).data,
            'CONFIRMED': OrderListSerializer(
                confirmed_orders,
                many=True,
                context={'request': request}
            ).data,
            'PREPARING': OrderListSerializer(
                preparing_orders,
                many=True,
                context={'request': request}
            ).data,
            'READY': OrderListSerializer(
                ready_orders,
                many=True,
                context={'request': request}
            ).data,
        })
