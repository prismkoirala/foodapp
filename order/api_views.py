from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.exceptions import PermissionDenied

from order.models import Order, OrderItem, RestaurantTable
from order.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    RestaurantTableSerializer,
    RestaurantTableAdminSerializer,
    OrderAdminSerializer,
    OrderItemSerializer,
    OrderItemStatusUpdateSerializer,
    OrderItemCreateSerializer,
    OrderCheckoutSerializer,
)


# ────────────────────────────────────────────────
# Custom Permissions
# ────────────────────────────────────────────────

class IsManagerOrOwner(BasePermission):
    """
    Permission check for Manager or Owner roles only.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ('MANAGER', 'OWNER')


class IsOrderStaff(BasePermission):
    """
    Permission check for Waiter, Staff, Cook, Manager, or Owner roles.
    Orders can be created/accessed by waiter/staff/cook and also managers/owners.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ('WAITER', 'STAFF', 'COOK', 'MANAGER', 'OWNER')


class IsManagerOrOwnerOrWaiter(BasePermission):
    """
    Permission check for Manager, Owner, or Waiter roles.
    Tables can be accessed by waiter and also managers/owners.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ('MANAGER', 'OWNER', 'WAITER')


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
        qs = Order.objects.filter(
            restaurant__managers_and_staff=user
        ).select_related(
            'restaurant',
            'table',
        ).prefetch_related(
            'items__menu_item',
        )

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
        return Order.objects.filter(
            restaurant__managers_and_staff=user
        ).select_related(
            'restaurant',
            'table',
        ).prefetch_related(
            'items__menu_item',
        )


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
        user = self.request.user

        # Role-based status transitions
        if user.role == 'COOK':
            # Cook can only change confirmed to cooking
            if instance.status != Order.STATUS_CONFIRMED or new_status != Order.STATUS_COOKING:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'status': f"Cooks can only change orders from 'confirmed' to 'cooking'."})
        elif user.role in ('MANAGER', 'OWNER', 'WAITER'):
            # Manager, Owner, Waiter can change any status (full workflow access)
            # No restrictions - they can advance any order status
            pass
        elif user.role == 'STAFF':
            # Staff can only change cooking to checkout
            if instance.status != Order.STATUS_COOKING or new_status != Order.STATUS_CHECKOUT:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'status': f"Staff can only change orders from 'cooking' to 'checkout'."})
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'status': "You don't have permission to update order status."})

        serializer.save()


# ────────────────────────────────────────────────
# Admin Views - Table CRUD (Manager/Owner only)
# ────────────────────────────────────────────────

class RestaurantTableListAdmin(generics.ListCreateAPIView):
    """
    Admin view - List and create restaurant tables
    Accessible by Manager, Owner, and Waiter roles
    """
    queryset = RestaurantTable.objects.all()
    serializer_class = RestaurantTableAdminSerializer
    permission_classes = [IsAuthenticated, IsManagerOrOwnerOrWaiter]

    def get_queryset(self):
        user = self.request.user
        qs = RestaurantTable.objects.filter(restaurant__managers_and_staff=user)

        restaurant_id = self.request.query_params.get('restaurant', None)
        if restaurant_id is not None:
            qs = qs.filter(restaurant_id=restaurant_id)

        return qs.order_by('name', 'id')

    def perform_create(self, serializer):
        user = self.request.user
        restaurant = serializer.validated_data.get('restaurant')

        if not restaurant.managers_and_staff.filter(id=user.id).exists():
            raise PermissionDenied("You don't have permission to add tables to this restaurant.")

        serializer.save()


class RestaurantTableDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin view - Manage single restaurant table
    Accessible by Manager, Owner, and Waiter roles
    """
    queryset = RestaurantTable.objects.all()
    serializer_class = RestaurantTableAdminSerializer
    permission_classes = [IsAuthenticated, IsManagerOrOwnerOrWaiter]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        return RestaurantTable.objects.filter(restaurant__managers_and_staff=user)

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user

        if not instance.restaurant.managers_and_staff.filter(id=user.id).exists():
            raise PermissionDenied("You don't have permission to update this table.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if not instance.restaurant.managers_and_staff.filter(id=user.id).exists():
            raise PermissionDenied("You don't have permission to delete this table.")

        instance.delete()


# ────────────────────────────────────────────────
# Admin Views - Order CRUD (Waiter/Cashier/Manager/Owner)
# ────────────────────────────────────────────────

class OrderListAdmin(generics.ListCreateAPIView):
    """
    Admin view - List and create orders
    Accessible by Waiter, Staff, Manager, and Owner roles
    
    Role-based filtering:
    - MANAGER/OWNER: Can see all orders including completed
    - WAITER/STAFF: Can only see in-progress orders (confirmed, cooking, checkout)
    """
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsOrderStaff]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.filter(
            restaurant__managers_and_staff=user
        ).select_related(
            'restaurant',
            'table',
            'created_by',
        ).prefetch_related(
            'items__menu_item',
        )

        # Role-based filtering: Waiter/Staff/Cook cannot see completed orders
        if user.role in ('WAITER', 'STAFF', 'COOK'):
            qs = qs.exclude(status='completed')

        restaurant_id = self.request.query_params.get('restaurant', None)
        if restaurant_id is not None:
            qs = qs.filter(restaurant_id=restaurant_id)

        status_param = self.request.query_params.get('status', None)
        if status_param is not None:
            qs = qs.filter(status=status_param)

        table_id = self.request.query_params.get('table', None)
        if table_id is not None:
            qs = qs.filter(table_id=table_id)

        # Nepali date filtering for day book
        nepali_date = self.request.query_params.get('nepali_date', None)
        if nepali_date is not None:
            qs = qs.filter(nepali_date=nepali_date)

        nepali_year = self.request.query_params.get('nepali_year', None)
        if nepali_year is not None:
            qs = qs.filter(nepali_year=nepali_year)

        nepali_month = self.request.query_params.get('nepali_month', None)
        if nepali_month is not None:
            qs = qs.filter(nepali_month=nepali_month)

        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderAdminSerializer

    def perform_create(self, serializer):
        user = self.request.user
        restaurant = serializer.validated_data.get('restaurant')

        if not restaurant.managers_and_staff.filter(id=user.id).exists():
            raise PermissionDenied("You don't have permission to create orders for this restaurant.")

        serializer.save()


class OrderDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin view - Manage single order
    Accessible by Waiter, Cashier, Manager, and Owner roles
    """
    queryset = Order.objects.all()
    serializer_class = OrderAdminSerializer
    permission_classes = [IsAuthenticated, IsOrderStaff]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            restaurant__managers_and_staff=user
        ).select_related(
            'restaurant',
            'table',
            'created_by',
        ).prefetch_related(
            'items__menu_item',
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user

        if not instance.restaurant.managers_and_staff.filter(id=user.id).exists():
            raise PermissionDenied("You don't have permission to update this order.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if not instance.restaurant.managers_and_staff.filter(id=user.id).exists():
            raise PermissionDenied("You don't have permission to delete this order.")

        instance.delete()


# ────────────────────────────────────────────────
# Order Item Management Views
# ────────────────────────────────────────────────

class OrderItemStatusUpdateView(generics.UpdateAPIView):
    """
    Update individual order item status
    Accessible by Cook, Staff, Manager, Owner, Waiter
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsOrderStaff]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        return OrderItem.objects.filter(order__restaurant__managers_and_staff=user)

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        
        # Role-based item status transitions
        if user.role == 'COOK':
            # Cook can only change pending to preparing, and preparing to ready
            old_status = instance.status
            new_status = serializer.validated_data['status']
            
            if old_status == OrderItem.STATUS_PENDING and new_status == OrderItem.STATUS_PREPARING:
                pass  # Allowed
            elif old_status == OrderItem.STATUS_PREPARING and new_status == OrderItem.STATUS_READY:
                pass  # Allowed
            else:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'status': "Cooks can only change: pending → preparing, preparing → ready"})
                
        elif user.role == 'STAFF':
            # Staff can only change ready to served
            old_status = instance.status
            new_status = serializer.validated_data['status']
            
            if old_status == OrderItem.STATUS_READY and new_status == OrderItem.STATUS_SERVED:
                pass  # Allowed
            else:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'status': "Staff can only change: ready → served"})
                
        elif user.role in ('MANAGER', 'OWNER', 'WAITER', 'CASHIER'):
            # Manager, Owner, Waiter, Cashier can change any status
            pass
            
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'status': "You don't have permission to update item status."})
        
        serializer.save()
        
        # Note: Order is NOT auto-completed when all items are served
        # Order should only be marked as completed after billing is done via the billing modal


class OrderAddItemView(generics.CreateAPIView):
    """
    Add items to existing order
    Accessible by Waiter, Manager, Owner
    """
    serializer_class = OrderItemCreateSerializer
    permission_classes = [IsAuthenticated, IsManagerOrOwnerOrWaiter]

    def get_queryset(self):
        return OrderItem.objects.none()

    def perform_create(self, serializer):
        order_id = self.kwargs['order_id']
        user = self.request.user
        
        try:
            order = Order.objects.get(
                id=order_id,
                restaurant__managers_and_staff=user
            )
            
            if order.status == Order.STATUS_COMPLETED:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Cannot add items to completed orders.")
            
            menu_item = serializer.validated_data['menu_item']
            quantity = serializer.validated_data['quantity']
            unit_price = menu_item.price
            
            # Check if item already exists in order, update quantity
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                menu_item=menu_item,
                defaults={'quantity': quantity, 'unit_price': unit_price}
            )
            
            if not created:
                order_item.quantity += quantity
                order_item.save()
                
        except Order.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Order not found or you don't have permission to access it.")


class OrderCheckoutView(generics.UpdateAPIView):
    """
    Complete checkout with final_total and mark order as completed.
    Accessible by Manager, Owner, Cashier
    """
    queryset = Order.objects.all()
    serializer_class = OrderCheckoutSerializer
    permission_classes = [IsAuthenticated, IsOrderStaff]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(restaurant__managers_and_staff=user)

    def perform_update(self, serializer):
        # Save final_total and mark order as completed
        serializer.save(status=Order.STATUS_COMPLETED)
