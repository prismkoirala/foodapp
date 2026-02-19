# billing/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import SubscriptionPlan, RestaurantSubscription, PaymentMethod, BillingRecord, BillingInvoice
from .serializers import (
    SubscriptionPlanSerializer,
    RestaurantSubscriptionSerializer,
    PaymentMethodSerializer,
    BillingRecordSerializer,
    BillingInvoiceSerializer
)
from menu.models import Restaurant


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing subscription plans
    Only superusers can manage plans, others can only view
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    
    def get_queryset(self):
        """Filter active plans, but allow superusers to see all"""
        if self.request.user.is_superuser:
            return SubscriptionPlan.objects.all()
        return SubscriptionPlan.objects.filter(is_active=True)


class RestaurantSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing restaurant subscriptions
    """
    queryset = RestaurantSubscription.objects.all()
    serializer_class = RestaurantSubscriptionSerializer
    
    def get_queryset(self):
        """Filter subscriptions based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return RestaurantSubscription.objects.all()
        elif hasattr(user, 'managed_restaurants'):
            restaurant_ids = user.managed_restaurants.values_list('id', flat=True)
            return RestaurantSubscription.objects.filter(restaurant_id__in=restaurant_ids)
        else:
            return RestaurantSubscription.objects.none()
    
    def perform_create(self, serializer):
        """Set additional fields when creating subscription"""
        # Check if restaurant already has an active subscription
        restaurant_id = serializer.validated_data['restaurant_id']
        existing_subscription = RestaurantSubscription.objects.filter(
            restaurant_id=restaurant_id,
            status__in=['ACTIVE', 'TRIAL']
        ).first()
        
        if existing_subscription:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Restaurant already has an active subscription")
        
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a subscription"""
        subscription = self.get_object()
        subscription.status = 'CANCELLED'
        subscription.cancelled_at = timezone.now()
        subscription.auto_renew = False
        subscription.save()
        
        # Create a billing record for the cancellation
        BillingRecord.objects.create(
            subscription=subscription,
            amount=0,
            currency='USD',
            billing_cycle=subscription.billing_cycle,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            status='CANCELLED'
        )
        
        return Response({'status': 'subscription cancelled'})
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reactivate a cancelled subscription"""
        subscription = self.get_object()
        
        if subscription.status not in ['CANCELLED', 'EXPIRED']:
            return Response(
                {'error': 'Can only reactivate cancelled or expired subscriptions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription.status = 'ACTIVE'
        subscription.cancelled_at = None
        subscription.auto_renew = True
        subscription.current_period_end = timezone.now() + timezone.timedelta(days=30)
        subscription.save()
        
        return Response({'status': 'subscription reactivated'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get subscription statistics"""
        if not request.user.is_superuser:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        total = RestaurantSubscription.objects.count()
        active = RestaurantSubscription.objects.filter(status='ACTIVE').count()
        trial = RestaurantSubscription.objects.filter(status='TRIAL').count()
        expired = RestaurantSubscription.objects.filter(status='EXPIRED').count()
        cancelled = RestaurantSubscription.objects.filter(status='CANCELLED').count()
        
        return Response({
            'total_subscriptions': total,
            'active_subscriptions': active,
            'trial_subscriptions': trial,
            'expired_subscriptions': expired,
            'cancelled_subscriptions': cancelled
        })


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment methods
    """
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    
    def get_queryset(self):
        """Filter payment methods based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return PaymentMethod.objects.all()
        elif hasattr(user, 'managed_restaurants'):
            restaurant_ids = user.managed_restaurants.values_list('id', flat=True)
            return PaymentMethod.objects.filter(restaurant_id__in=restaurant_ids)
        else:
            return PaymentMethod.objects.none()
    
    def perform_create(self, serializer):
        """Ensure only one default payment method per restaurant"""
        restaurant_id = serializer.validated_data['restaurant_id']
        is_default = serializer.validated_data.get('is_default', False)
        
        if is_default:
            # Unset other default methods for this restaurant
            PaymentMethod.objects.filter(
                restaurant_id=restaurant_id,
                is_default=True
            ).update(is_default=False)
        
        serializer.save()


class BillingRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing billing records
    """
    queryset = BillingRecord.objects.all()
    serializer_class = BillingRecordSerializer
    
    def get_queryset(self):
        """Filter billing records based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return BillingRecord.objects.all()
        elif hasattr(user, 'managed_restaurants'):
            restaurant_ids = user.managed_restaurants.values_list('id', flat=True)
            return BillingRecord.objects.filter(
                subscription__restaurant_id__in=restaurant_ids
            )
        else:
            return BillingRecord.objects.none()
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a billing record as paid"""
        record = self.get_object()
        record.status = 'PAID'
        record.paid_at = timezone.now()
        record.save()
        
        return Response({'status': 'marked as paid'})
    
    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """Mark a billing record as failed"""
        record = self.get_object()
        record.status = 'FAILED'
        record.failed_at = timezone.now()
        record.failure_reason = request.data.get('reason', 'Payment failed')
        record.save()
        
        return Response({'status': 'marked as failed'})


class BillingInvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing billing invoices
    """
    queryset = BillingInvoice.objects.all()
    serializer_class = BillingInvoiceSerializer
    
    def get_queryset(self):
        """Filter invoices based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return BillingInvoice.objects.all()
        elif hasattr(user, 'managed_restaurants'):
            restaurant_ids = user.managed_restaurants.values_list('id', flat=True)
            return BillingInvoice.objects.filter(
                billing_record__subscription__restaurant_id__in=restaurant_ids
            )
        else:
            return BillingInvoice.objects.none()
    
    def perform_create(self, serializer):
        """Generate invoice number automatically"""
        last_invoice = BillingInvoice.objects.order_by('-id').first()
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            new_number = f"INV-{last_number + 1:06d}"
        else:
            new_number = "INV-000001"
        
        serializer.save(invoice_number=new_number)
    
    @action(detail=True, methods=['post'])
    def mark_sent(self, request, pk=None):
        """Mark invoice as sent"""
        invoice = self.get_object()
        invoice.is_sent = True
        invoice.sent_at = timezone.now()
        invoice.save()
        
        return Response({'status': 'marked as sent'})


# Additional API Views for dropdown data
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class RestaurantDropdownView(APIView):
    """
    API view to get restaurants for dropdown
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if user.is_superuser:
            restaurants = Restaurant.objects.all()
        elif hasattr(user, 'managed_restaurants'):
            restaurant_ids = user.managed_restaurants.values_list('id', flat=True)
            restaurants = Restaurant.objects.filter(id__in=restaurant_ids)
        else:
            restaurants = Restaurant.objects.none()
        
        data = [
            {
                'id': restaurant.id,
                'name': restaurant.name,
                'address': restaurant.address or ''
            }
            for restaurant in restaurants
        ]
        
        return Response(data)


class SubscriptionPlanDropdownView(APIView):
    """
    API view to get active subscription plans for dropdown
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        
        data = [
            {
                'id': plan.id,
                'name': plan.name,
                'monthly_price': str(plan.monthly_price),
                'yearly_price': str(plan.yearly_price),
                'bi_yearly_price': str(plan.bi_yearly_price),
                'max_menu_items': plan.max_menu_items,
                'max_categories': plan.max_categories,
                'max_menu_groups': plan.max_menu_groups,
                'max_staff_users': plan.max_staff_users,
                'features': plan.features
            }
            for plan in plans
        ]
        
        return Response(data)
