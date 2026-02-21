# billing/serializers.py
from rest_framework import serializers
from .models import SubscriptionPlan, RestaurantSubscription, PaymentMethod, BillingRecord, BillingInvoice
from menu.models import Restaurant


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for SubscriptionPlan model"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'name',
            'monthly_price',
            'yearly_price',
            'bi_yearly_price',
            'max_menu_items',
            'max_categories',
            'max_menu_groups',
            'max_staff_users',
            'features',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RestaurantSerializer(serializers.ModelSerializer):
    """Simple serializer for Restaurant data"""
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address']


class RestaurantSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for RestaurantSubscription model"""
    restaurant = RestaurantSerializer(read_only=True)
    plan = SubscriptionPlanSerializer(read_only=True)
    restaurant_id = serializers.IntegerField(write_only=True)
    plan_id = serializers.IntegerField(write_only=True)
    
    # Computed fields
    is_active = serializers.ReadOnlyField()
    is_trial = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    
    class Meta:
        model = RestaurantSubscription
        fields = [
            'id',
            'restaurant',
            'restaurant_id',
            'plan',
            'plan_id',
            'billing_cycle',
            'status',
            'trial_end_date',
            'current_period_start',
            'current_period_end',
            'cancelled_at',
            'price_at_subscription',
            'discount_percentage',
            'discount_amount',
            'final_price',
            'auto_renew',
            'is_active',
            'is_trial',
            'days_until_expiry',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'is_active',
            'is_trial',
            'days_until_expiry',
            'final_price'
        ]

    def validate_restaurant_id(self, value):
        """Validate that restaurant exists"""
        try:
            Restaurant.objects.get(id=value)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("Restaurant not found")
        return value

    def validate_plan_id(self, value):
        """Validate that plan exists and is active"""
        try:
            plan = SubscriptionPlan.objects.get(id=value)
            if not plan.is_active:
                raise serializers.ValidationError("This plan is not active")
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Subscription plan not found")
        return value

    def validate(self, attrs):
        """Validate discount fields"""
        discount_percentage = attrs.get('discount_percentage', 0)
        discount_amount = attrs.get('discount_amount', 0)
        
        # Validate that only one type of discount is applied
        if discount_percentage > 0 and discount_amount > 0:
            raise serializers.ValidationError(
                "Cannot apply both percentage and fixed amount discount simultaneously"
            )
        
        # Validate discount percentage range
        if discount_percentage < 0 or discount_percentage > 100:
            raise serializers.ValidationError(
                "Discount percentage must be between 0 and 100"
            )
        
        # Validate discount amount
        if discount_amount < 0:
            raise serializers.ValidationError(
                "Discount amount cannot be negative"
            )
        
        return super().validate(attrs)

    def create(self, validated_data):
        """Create a new restaurant subscription"""
        restaurant_id = validated_data.pop('restaurant_id')
        plan_id = validated_data.pop('plan_id')
        
        restaurant = Restaurant.objects.get(id=restaurant_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)
        
        # Set price based on billing cycle
        if validated_data['billing_cycle'] == 'MONTHLY':
            base_price = plan.monthly_price
        elif validated_data['billing_cycle'] == 'YEARLY':
            base_price = plan.yearly_price
        else:  # BI_YEARLY
            base_price = plan.bi_yearly_price
        
        validated_data['price_at_subscription'] = base_price
        
        # Calculate final price with discount
        discount_percentage = validated_data.get('discount_percentage', 0)
        discount_amount = validated_data.get('discount_amount', 0)
        
        from decimal import Decimal
        
        if discount_amount > 0:
            # Fixed amount discount takes priority
            final_price = max(Decimal('0.00'), base_price - Decimal(str(discount_amount)))
        elif discount_percentage > 0:
            # Percentage discount
            final_price = base_price * (Decimal('1.00') - (Decimal(str(discount_percentage)) / Decimal('100.00')))
        else:
            final_price = base_price
        
        # Set period dates
        from django.utils import timezone
        import datetime
        
        now = timezone.now()
        validated_data['current_period_start'] = now
        
        if validated_data['billing_cycle'] == 'MONTHLY':
            validated_data['current_period_end'] = now + datetime.timedelta(days=30)
        elif validated_data['billing_cycle'] == 'YEARLY':
            validated_data['current_period_end'] = now + datetime.timedelta(days=365)
        else:  # BI_YEARLY
            validated_data['current_period_end'] = now + datetime.timedelta(days=730)
        
        # Set trial end date if status is TRIAL
        if validated_data.get('status') == 'TRIAL':
            validated_data['trial_end_date'] = now + datetime.timedelta(days=14)
        
        return RestaurantSubscription.objects.create(
            restaurant=restaurant,
            plan=plan,
            **validated_data
        )


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model"""
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id',
            'restaurant',
            'restaurant_id',
            'method_type',
            'is_default',
            'is_active',
            'card_brand',
            'card_last_four',
            'card_expiry_month',
            'card_expiry_year',
            'stripe_customer_id',
            'stripe_payment_method_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at'
        ]


class BillingRecordSerializer(serializers.ModelSerializer):
    """Serializer for BillingRecord model"""
    subscription = RestaurantSubscriptionSerializer(read_only=True)
    subscription_id = serializers.IntegerField(write_only=True)
    
    # Payment method as string field (from choices)
    payment_method_display = serializers.SerializerMethodField()
    
    def get_payment_method_display(self, obj):
        """Get display text for payment method"""
        return obj.get_payment_method_display()
    
    # Computed fields
    total_amount = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = BillingRecord
        fields = [
            'id',
            'subscription',
            'subscription_id',
            'description',
            'amount',
            'currency',
            'billing_cycle',
            'period_start',
            'period_end',
            'status',
            'payment_method',
            'payment_method_display',
            'transaction_id',
            'paid_at',
            'failed_at',
            'failure_reason',
            'discount_amount',
            'tax_amount',
            'total_amount',
            'is_overdue',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'total_amount',
            'is_overdue'
        ]


class BillingInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for BillingInvoice model"""
    billing_record = BillingRecordSerializer(read_only=True)
    billing_record_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = BillingInvoice
        fields = [
            'id',
            'billing_record',
            'billing_record_id',
            'invoice_number',
            'invoice_date',
            'due_date',
            'billing_address',
            'notes',
            'terms_and_conditions',
            'pdf_file',
            'is_sent',
            'sent_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'invoice_number',
            'created_at',
            'updated_at'
        ]
