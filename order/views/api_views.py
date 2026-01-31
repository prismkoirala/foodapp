from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from menu.models import Restaurant
from order.models import Order, RestaurantTable
from order.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    RestaurantTableSerializer,
)


class RestaurantTableListCreate(generics.ListCreateAPIView):
    queryset = RestaurantTable.objects.all()
    serializer_class = RestaurantTableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = RestaurantTable.objects.filter(restaurant__managers_and_staff=user)

        restaurant_id = self.request.query_params.get('restaurant', None)
        if restaurant_id is not None:
            qs = qs.filter(restaurant_id=restaurant_id)

        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')

        return qs.order_by('name', 'id')

    def perform_create(self, serializer):
        user = self.request.user
        restaurant = serializer.validated_data.get('restaurant')

        if not restaurant.managers_and_staff.filter(id=user.id).exists():
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You don't have permission to add tables to this restaurant.")

        serializer.save()


class OrderListCreate(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.filter(restaurant__managers_and_staff=user).prefetch_related('items')

        restaurant_id = self.request.query_params.get('restaurant', None)
        if restaurant_id is not None:
            qs = qs.filter(restaurant_id=restaurant_id)

        status_param = self.request.query_params.get('status', None)
        if status_param is not None:
            qs = qs.filter(status=status_param)

        table_id = self.request.query_params.get('table', None)
        if table_id is not None:
            qs = qs.filter(table_id=table_id)

        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        user = self.request.user
        restaurant = serializer.validated_data.get('restaurant')

        if not restaurant.managers_and_staff.filter(id=user.id).exists():
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You don't have permission to create orders for this restaurant.")

        serializer.save()


class OrderDetail(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(restaurant__managers_and_staff=user).prefetch_related('items')


class OrderStatusUpdate(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(restaurant__managers_and_staff=user)

    def perform_update(self, serializer):
        instance = self.get_object()
        new_status = serializer.validated_data.get('status')

        allowed_next = {
            Order.STATUS_CONFIRMED: {Order.STATUS_COOKING, Order.STATUS_CHECKOUT},
            Order.STATUS_COOKING: {Order.STATUS_CHECKOUT},
            Order.STATUS_CHECKOUT: {Order.STATUS_COMPLETED},
            Order.STATUS_COMPLETED: set(),
        }

        if new_status not in allowed_next.get(instance.status, set()):
            from rest_framework.exceptions import ValidationError

            raise ValidationError({'status': f"Invalid transition from '{instance.status}' to '{new_status}'."})

        serializer.save()
