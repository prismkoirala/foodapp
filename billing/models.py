# billing/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import timedelta
from menu.models import Restaurant


class SubscriptionPlan(models.Model):
    """
    Subscription plans available for restaurants
    """
    PLAN_CHOICES = [
        ('BASIC', _('Basic')),
        ('GOLD', _('Gold')),
        ('PLATINUM', _('Platinum')),
    ]
    
    name = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        unique=True,
        verbose_name=_('Plan Name')
    )
    
    # Pricing options
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Monthly Price'),
        help_text=_('Price for monthly billing cycle')
    )
    
    yearly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Yearly Price'),
        help_text=_('Price for yearly billing cycle (12 months)')
    )
    
    bi_yearly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Bi-Yearly Price'),
        help_text=_('Price for bi-yearly billing cycle (24 months)')
    )
    
    # Features and limits
    max_menu_items = models.PositiveIntegerField(
        default=50,
        verbose_name=_('Max Menu Items'),
        help_text=_('Maximum number of menu items allowed')
    )
    
    max_categories = models.PositiveIntegerField(
        default=10,
        verbose_name=_('Max Categories'),
        help_text=_('Maximum number of categories allowed')
    )
    
    max_menu_groups = models.PositiveIntegerField(
        default=3,
        verbose_name=_('Max Menu Groups'),
        help_text=_('Maximum number of menu groups allowed')
    )
    
    max_staff_users = models.PositiveIntegerField(
        default=2,
        verbose_name=_('Max Staff Users'),
        help_text=_('Maximum number of staff users allowed')
    )
    
    features = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_('Features'),
        help_text=_('JSON object containing plan features')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.get_name_display()} Plan"
    
    def get_price_for_cycle(self, billing_cycle):
        """Get price based on billing cycle"""
        if billing_cycle == 'MONTHLY':
            return self.monthly_price
        elif billing_cycle == 'YEARLY':
            return self.yearly_price
        elif billing_cycle == 'BI_YEARLY':
            return self.bi_yearly_price
        return self.monthly_price
    
    def get_cycle_duration_months(self, billing_cycle):
        """Get duration in months for billing cycle"""
        if billing_cycle == 'MONTHLY':
            return 1
        elif billing_cycle == 'YEARLY':
            return 12
        elif billing_cycle == 'BI_YEARLY':
            return 24
        return 1


class RestaurantSubscription(models.Model):
    """
    Restaurant's current subscription
    """
    BILLING_CYCLE_CHOICES = [
        ('MONTHLY', _('Monthly')),
        ('YEARLY', _('Yearly')),
        ('BI_YEARLY', _('Bi-Yearly')),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', _('Active')),
        ('EXPIRED', _('Expired')),
        ('CANCELLED', _('Cancelled')),
        ('SUSPENDED', _('Suspended')),
        ('TRIAL', _('Trial')),
    ]
    
    restaurant = models.OneToOneField(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name=_('Restaurant')
    )
    
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        verbose_name=_('Subscription Plan')
    )
    
    billing_cycle = models.CharField(
        max_length=10,
        choices=BILLING_CYCLE_CHOICES,
        default='MONTHLY',
        verbose_name=_('Billing Cycle')
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='TRIAL',
        verbose_name=_('Status')
    )
    
    # Dates
    trial_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Trial End Date')
    )
    
    current_period_start = models.DateTimeField(
        verbose_name=_('Current Period Start')
    )
    
    current_period_end = models.DateTimeField(
        verbose_name=_('Current Period End')
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Cancelled At')
    )
    
    # Pricing at time of subscription (to handle price changes)
    price_at_subscription = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Price at Subscription')
    )
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default='0.00',
        verbose_name=_('Discount Percentage'),
        help_text=_('Discount percentage (e.g., 25.00 for 25% discount)')
    )
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default='0.00',
        verbose_name=_('Discount Amount'),
        help_text=_('Fixed discount amount (overrides percentage if set)')
    )
    final_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default='0.00',
        verbose_name=_('Final Price'),
        help_text=_('Final price after discount')
    )
    
    auto_renew = models.BooleanField(
        default=True,
        verbose_name=_('Auto Renew')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Restaurant Subscription')
        verbose_name_plural = _('Restaurant Subscriptions')
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.plan.name} ({self.get_status_display()})"
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        from django.utils import timezone
        return (
            self.status == 'ACTIVE' and 
            self.current_period_end > timezone.now()
        )
    
    @property
    def is_trial(self):
        """Check if subscription is in trial period"""
        from django.utils import timezone
        return (
            self.status == 'TRIAL' and 
            self.trial_end_date and 
            self.trial_end_date > timezone.now()
        )

    @property
    def days_until_expiry(self):
        """Calculate days until subscription expires"""
        from django.utils import timezone
        if self.current_period_end:
            delta = self.current_period_end - timezone.now()
            return max(0, delta.days)
        return 0

    @property
    def calculate_final_price(self):
        """
        Calculate final price after discount
        Priority: discount_amount > discount_percentage
        """
        base_price = self.price_at_subscription
        
        # Convert discount values to Decimal for comparison
        discount_amount = Decimal(str(self.discount_amount)) if self.discount_amount else Decimal('0.00')
        discount_percentage = Decimal(str(self.discount_percentage)) if self.discount_percentage else Decimal('0.00')
        
        if discount_amount > Decimal('0.00'):
            # Fixed amount discount takes priority
            final_price = max(Decimal('0.00'), base_price - discount_amount)
        elif discount_percentage > Decimal('0.00'):
            # Percentage discount
            final_price = base_price * (Decimal('1.00') - (discount_percentage / Decimal('100.00')))
        else:
            final_price = base_price
        
        return final_price.quantize(Decimal('0.01'))

    def calculate_savings(self):
        """Calculate total savings from discount"""
        return (self.price_at_subscription - self.final_price).quantize(Decimal('0.01'))

    def get_discount_display(self):
        """Get human-readable discount description"""
        if self.discount_amount > 0:
            return f"${self.discount_amount} off"
        elif self.discount_percentage > 0:
            return f"{self.discount_percentage}% off"
        return "No discount"

    def save(self, *args, **kwargs):
        """
        Override save to calculate final price before saving
        """
        # Ensure price_at_subscription is set
        if not self.price_at_subscription or self.price_at_subscription == Decimal('0.00'):
            if self.plan:
                # Set price based on billing cycle
                if self.billing_cycle == 'MONTHLY':
                    self.price_at_subscription = self.plan.monthly_price
                elif self.billing_cycle == 'YEARLY':
                    self.price_at_subscription = self.plan.yearly_price
                else:  # BI_YEARLY
                    self.price_at_subscription = self.plan.bi_yearly_price
        
        # Always calculate final price
        self.final_price = self.calculate_final_price
        
        super().save(*args, **kwargs)

    def renew_subscription(self):
        """Renew subscription for next billing cycle"""
        from django.utils import timezone
        import datetime
        
        if not self.auto_renew or self.status == 'CANCELLED':
            return False
        
        # Calculate next period end date
        months = self.plan.get_cycle_duration_months(self.billing_cycle)
        next_end = self.current_period_end + datetime.timedelta(days=30 * months)
        
        # Create billing record
        BillingRecord.objects.create(
            subscription=self,
            amount=self.plan.get_price_for_cycle(self.billing_cycle),
            billing_cycle=self.billing_cycle,
            period_start=self.current_period_end,
            period_end=next_end,
            status='PENDING'
        )
        
        # Update subscription
        self.current_period_start = self.current_period_end
        self.current_period_end = next_end
        self.status = 'ACTIVE'
        self.save()
        
        return True


class BillingRecord(models.Model):
    """
    Individual billing records for each billing cycle
    """
    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PAID', _('Paid')),
        ('FAILED', _('Failed')),
        ('REFUNDED', _('Refunded')),
        ('CANCELLED', _('Cancelled')),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('MONTHLY', _('Monthly')),
        ('YEARLY', _('Yearly')),
        ('BI_YEARLY', _('Bi-Yearly')),
        ('ONE_TIME', _('One-Time')),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('STRIPE', _('Stripe')),
        ('PAYPAL', _('PayPal')),
        ('BANK_TRANSFER', _('Bank Transfer')),
        ('CASH', _('Cash')),
        ('OTHER', _('Other')),
    ]
    
    subscription = models.ForeignKey(
        RestaurantSubscription,
        on_delete=models.CASCADE,
        related_name='billing_records',
        verbose_name=_('Subscription')
    )
    
    # Billing details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Amount')
    )
    
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Description of the billing item (e.g., "Setup Fee", "Custom Feature")')
    )
    
    currency = models.CharField(
        max_length=3,
        default='NPR',
        verbose_name=_('Currency')
    )
    
    billing_cycle = models.CharField(
        max_length=10,
        choices=BILLING_CYCLE_CHOICES,
        verbose_name=_('Billing Cycle')
    )
    
    # Period (optional for one-time payments)
    period_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Period Start'),
        help_text=_('Required for recurring payments, optional for one-time payments')
    )
    
    period_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Period End'),
        help_text=_('Required for recurring payments, optional for one-time payments')
    )
    
    # Payment details
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name=_('Status')
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        verbose_name=_('Payment Method')
    )
    
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Transaction ID'),
        help_text=_('External payment system transaction ID')
    )
    
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Paid At')
    )
    
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Failed At')
    )
    
    failure_reason = models.TextField(
        blank=True,
        verbose_name=_('Failure Reason')
    )
    
    # Discounts and taxes
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default='0.00',
        verbose_name=_('Discount Amount')
    )
    
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default='0.00',
        verbose_name=_('Tax Amount')
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Total Amount')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Billing Record')
        verbose_name_plural = _('Billing Records')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subscription.restaurant.name} - {self.amount} {self.currency} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Calculate total amount if not set
        if not self.total_amount:
            # Ensure all values are Decimal for arithmetic
            amount = Decimal(str(self.amount)) if self.amount else Decimal('0.00')
            discount_amount = Decimal(str(self.discount_amount)) if self.discount_amount else Decimal('0.00')
            tax_amount = Decimal(str(self.tax_amount)) if self.tax_amount else Decimal('0.00')
            
            self.total_amount = amount - discount_amount + tax_amount
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if payment is overdue (only applicable to recurring payments)"""
        from django.utils import timezone
        # One-time payments cannot be overdue
        if self.billing_cycle == 'ONE_TIME':
            return False
        return (
            self.status == 'PENDING' and 
            self.period_end and 
            self.period_end < timezone.now()
        )

    @classmethod
    def create_one_time_payment(cls, subscription, amount, description, **kwargs):
        """
        Convenience method to create a one-time payment record
        
        Args:
            subscription: RestaurantSubscription instance
            amount: Decimal amount to charge
            description: Description of the payment (e.g., "Setup Fee")
            **kwargs: Additional fields (payment_method, etc.)
        
        Returns:
            BillingRecord instance
        """
        from django.utils import timezone
        
        return cls.objects.create(
            subscription=subscription,
            amount=amount,
            description=description,
            billing_cycle='ONE_TIME',
            period_start=None,
            period_end=None,
            **kwargs
        )


class PaymentMethod(models.Model):
    """
    Payment methods for restaurants
    """
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='payment_methods',
        verbose_name=_('Restaurant')
    )
    
    method_type = models.CharField(
        max_length=20,
        choices=BillingRecord.PAYMENT_METHOD_CHOICES,
        verbose_name=_('Method Type')
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('Is Default')
    )
    
    # Stripe specific fields
    stripe_customer_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Stripe Customer ID')
    )
    
    stripe_payment_method_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Stripe Payment Method ID')
    )
    
    # Card details (encrypted or from payment provider)
    card_last_four = models.CharField(
        max_length=4,
        blank=True,
        verbose_name=_('Card Last Four')
    )
    
    card_brand = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Card Brand')
    )
    
    card_expiry_month = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Card Expiry Month')
    )
    
    card_expiry_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Card Expiry Year')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.method_type == 'STRIPE' and self.card_last_four:
            return f"{self.card_brand} ****{self.card_last_four}"
        return f"{self.get_method_type_display()}"


class BillingInvoice(models.Model):
    """
    Invoice documents for billing records
    """
    billing_record = models.OneToOneField(
        BillingRecord,
        on_delete=models.CASCADE,
        related_name='invoice',
        verbose_name=_('Billing Record')
    )
    
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Invoice Number')
    )
    
    invoice_date = models.DateField(
        verbose_name=_('Invoice Date')
    )
    
    due_date = models.DateField(
        verbose_name=_('Due Date')
    )
    
    # Billing address
    billing_address = models.TextField(
        verbose_name=_('Billing Address')
    )
    
    # Notes and terms
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    terms_and_conditions = models.TextField(
        blank=True,
        verbose_name=_('Terms and Conditions')
    )
    
    # File
    pdf_file = models.FileField(
        upload_to='invoices/',
        null=True,
        blank=True,
        verbose_name=_('PDF File')
    )
    
    is_sent = models.BooleanField(
        default=False,
        verbose_name=_('Is Sent')
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Sent At')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Billing Invoice')
        verbose_name_plural = _('Billing Invoices')
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.billing_record.subscription.restaurant.name}"
    
    def save(self, *args, **kwargs):
        # Generate invoice number if not set
        if not self.invoice_number:
            from django.utils import timezone
            year = timezone.now().year
            month = timezone.now().month
            count = BillingInvoice.objects.filter(
                invoice_date__year=year,
                invoice_date__month=month
            ).count() + 1
            self.invoice_number = f"INV-{year}{month:02d}-{count:04d}"
        super().save(*args, **kwargs)
