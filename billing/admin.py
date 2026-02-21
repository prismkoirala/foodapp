# billing/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import (
    SubscriptionPlan, 
    RestaurantSubscription, 
    BillingRecord, 
    PaymentMethod, 
    BillingInvoice
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """
    Admin interface for Subscription Plans
    """
    list_display = (
        'name',
        'monthly_price',
        'yearly_price',
        'bi_yearly_price',
        'get_features_summary',
        'is_active',
        'created_at'
    )
    list_filter = ('is_active', 'name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('name', 'is_active')
        }),
        ('Pricing', {
            'fields': (
                'monthly_price',
                'yearly_price', 
                'bi_yearly_price'
            )
        }),
        ('Limits and Features', {
            'fields': (
                'max_menu_items',
                'max_categories',
                'max_menu_groups',
                'max_staff_users',
                'features'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_features_summary(self, obj):
        """Display summary of features"""
        if obj.features:
            features_list = []
            for key, value in obj.features.items():
                if isinstance(value, bool) and value:
                    features_list.append(key.replace('_', ' ').title())
                elif isinstance(value, str) and value:
                    features_list.append(f"{key}: {value}")
            return ', '.join(features_list[:3])  # Show first 3 features
        return 'No features set'
    get_features_summary.short_description = _('Features')


class BillingRecordInline(admin.TabularInline):
    """
    Inline billing records for subscription admin
    """
    model = BillingRecord
    extra = 0
    readonly_fields = ('created_at', 'total_amount')
    fields = (
        'amount',
        'currency',
        'billing_cycle',
        'status',
        'payment_method',
        'total_amount',
        'created_at'
    )


@admin.register(RestaurantSubscription)
class RestaurantSubscriptionAdmin(admin.ModelAdmin):
    """
    Admin interface for Restaurant Subscriptions
    """
    list_display = (
        'restaurant',
        'plan',
        'billing_cycle',
        'get_status_badge',
        'get_current_period',
        'get_days_remaining',
        'auto_renew',
        'created_at'
    )
    list_filter = (
        'status',
        'billing_cycle',
        'plan',
        'auto_renew',
        'created_at'
    )
    search_fields = ('restaurant__name', 'plan__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [BillingRecordInline]
    
    fieldsets = (
        ('Subscription Details', {
            'fields': (
                'restaurant',
                'plan',
                'billing_cycle',
                'status'
            )
        }),
        ('Period Information', {
            'fields': (
                'trial_end_date',
                'current_period_start',
                'current_period_end',
                'cancelled_at'
            )
        }),
        ('Billing Information', {
            'fields': (
                'price_at_subscription',
                'auto_renew'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'ACTIVE': 'green',
            'TRIAL': 'blue',
            'EXPIRED': 'red',
            'CANCELLED': 'orange',
            'SUSPENDED': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = _('Status')
    get_status_badge.admin_order_field = 'status'
    
    def get_current_period(self, obj):
        """Display current period dates"""
        if obj.current_period_start and obj.current_period_end:
            return f"{obj.current_period_start.strftime('%Y-%m-%d')} to {obj.current_period_end.strftime('%Y-%m-%d')}"
        return 'Not set'
    get_current_period.short_description = _('Current Period')
    
    def get_days_remaining(self, obj):
        """Display days until expiry"""
        days = obj.days_until_expiry
        if days <= 7 and days > 0:
            color = 'orange'
        elif days == 0:
            color = 'red'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} days</span>',
            color,
            days
        )
    get_days_remaining.short_description = _('Days Remaining')
    
    actions = ['extend_trial', 'cancel_subscription', 'reactivate_subscription']
    
    def extend_trial(self, request, queryset):
        """Extend trial period by 7 days"""
        updated = 0
        for subscription in queryset:
            if subscription.status == 'TRIAL':
                if subscription.trial_end_date:
                    subscription.trial_end_date = subscription.trial_end_date + timezone.timedelta(days=7)
                else:
                    subscription.trial_end_date = timezone.now() + timezone.timedelta(days=7)
                subscription.save()
                updated += 1
        self.message_user(request, f"Extended trial for {updated} subscriptions.")
    extend_trial.short_description = _('Extend trial by 7 days')
    
    def cancel_subscription(self, request, queryset):
        """Cancel selected subscriptions"""
        updated = queryset.update(
            status='CANCELLED',
            cancelled_at=timezone.now(),
            auto_renew=False
        )
        self.message_user(request, f"Cancelled {updated} subscriptions.")
    cancel_subscription.short_description = _('Cancel subscriptions')
    
    def reactivate_subscription(self, request, queryset):
        """Reactivate cancelled subscriptions"""
        updated = 0
        for subscription in queryset:
            if subscription.status in ['CANCELLED', 'EXPIRED']:
                subscription.status = 'ACTIVE'
                subscription.current_period_end = timezone.now() + timezone.timedelta(days=30)
                subscription.cancelled_at = None
                subscription.auto_renew = True
                subscription.save()
                updated += 1
        self.message_user(request, f"Reactivated {updated} subscriptions.")
    reactivate_subscription.short_description = _('Reactivate subscriptions')


@admin.register(BillingRecord)
class BillingRecordAdmin(admin.ModelAdmin):
    """
    Admin interface for Billing Records
    """
    list_display = (
        'subscription',
        'description',
        'amount',
        'currency',
        'total_amount',
        'billing_cycle',
        'get_status_badge',
        'payment_method',
        'get_period_dates',
        'is_overdue_status',
        'created_at'
    )
    list_filter = (
        'status',
        'payment_method',
        'billing_cycle',
        'currency',
        'created_at'
    )
    search_fields = (
        'subscription__restaurant__name',
        'transaction_id'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    
    fieldsets = (
        ('Billing Information', {
            'fields': (
                'subscription',
                'description',
                'amount',
                'currency',
                'billing_cycle',
                'total_amount'
            )
        }),
        ('Period', {
            'fields': ('period_start', 'period_end'),
            'description': 'Period dates are optional for one-time payments'
        }),
        ('Payment Details', {
            'fields': (
                'status',
                'payment_method',
                'transaction_id',
                'paid_at',
                'failed_at',
                'failure_reason'
            )
        }),
        ('Financial Details', {
            'fields': (
                'discount_amount',
                'tax_amount'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'PAID': 'green',
            'PENDING': 'orange',
            'FAILED': 'red',
            'REFUNDED': 'purple',
            'CANCELLED': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = _('Status')
    get_status_badge.admin_order_field = 'status'
    
    def get_period_dates(self, obj):
        """Display billing period"""
        if obj.billing_cycle == 'ONE_TIME':
            return "One-time payment"
        elif obj.period_start and obj.period_end:
            return f"{obj.period_start.strftime('%Y-%m-%d')} to {obj.period_end.strftime('%Y-%m-%d')}"
        else:
            return "No period set"
    get_period_dates.short_description = _('Period')
    
    def is_overdue_status(self, obj):
        """Display overdue status"""
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">OVERDUE</span>'
            )
        return format_html(
            '<span style="color: green;">On Time</span>'
        )
    is_overdue_status.short_description = _('Overdue')
    
    actions = ['mark_as_paid', 'mark_as_failed', 'generate_invoice']
    
    def mark_as_paid(self, request, queryset):
        """Mark selected records as paid"""
        updated = queryset.update(
            status='PAID',
            paid_at=timezone.now()
        )
        self.message_user(request, f"Marked {updated} records as paid.")
    mark_as_paid.short_description = _('Mark as paid')
    
    def mark_as_failed(self, request, queryset):
        """Mark selected records as failed"""
        updated = queryset.update(
            status='FAILED',
            failed_at=timezone.now()
        )
        self.message_user(request, f"Marked {updated} records as failed.")
    mark_as_failed.short_description = _('Mark as failed')
    
    def generate_invoice(self, request, queryset):
        """Generate invoices for selected records"""
        created = 0
        for record in queryset:
            if not hasattr(record, 'invoice'):
                BillingInvoice.objects.create(
                    billing_record=record,
                    invoice_date=timezone.now().date(),
                    due_date=timezone.now().date() + timezone.timedelta(days=30),
                    billing_address=record.subscription.restaurant.address or 'No address'
                )
                created += 1
        self.message_user(request, f"Generated {created} invoices.")
    generate_invoice.short_description = _('Generate invoices')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    Admin interface for Payment Methods
    """
    list_display = (
        'restaurant',
        'method_type',
        'get_card_display',
        'is_default',
        'is_active',
        'created_at'
    )
    list_filter = (
        'method_type',
        'is_default',
        'is_active',
        'created_at'
    )
    search_fields = ('restaurant__name', 'card_brand', 'card_last_four')
    ordering = ('-is_default', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Payment Method Details', {
            'fields': (
                'restaurant',
                'method_type',
                'is_default',
                'is_active'
            )
        }),
        ('Card Information', {
            'fields': (
                'card_brand',
                'card_last_four',
                'card_expiry_month',
                'card_expiry_year'
            )
        }),
        ('Stripe Integration', {
            'fields': (
                'stripe_customer_id',
                'stripe_payment_method_id'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_card_display(self, obj):
        """Display card information"""
        if obj.method_type == 'STRIPE' and obj.card_last_four:
            expiry = ""
            if obj.card_expiry_month and obj.card_expiry_year:
                expiry = f" ({obj.card_expiry_month:02d}/{obj.card_expiry_year})"
            return f"{obj.card_brand} ****{obj.card_last_four}{expiry}"
        return obj.get_method_type_display()
    get_card_display.short_description = _('Card Details')


@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    """
    Admin interface for Billing Invoices
    """
    list_display = (
        'invoice_number',
        'billing_record',
        'invoice_date',
        'due_date',
        'total_amount',
        'is_sent',
        'created_at'
    )
    list_filter = (
        'is_sent',
        'invoice_date',
        'due_date',
        'created_at'
    )
    search_fields = (
        'invoice_number',
        'billing_record__subscription__restaurant__name'
    )
    ordering = ('-invoice_date',)
    readonly_fields = ('invoice_number', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Invoice Information', {
            'fields': (
                'invoice_number',
                'billing_record',
                'invoice_date',
                'due_date'
            )
        }),
        ('Billing Details', {
            'fields': ('billing_address',)
        }),
        ('Content', {
            'fields': (
                'notes',
                'terms_and_conditions'
            )
        }),
        ('Document', {
            'fields': ('pdf_file',)
        }),
        ('Status', {
            'fields': ('is_sent', 'sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def total_amount(self, obj):
        """Display total amount from billing record"""
        return obj.billing_record.total_amount
    total_amount.short_description = _('Total Amount')
    
    actions = ['mark_as_sent', 'download_invoices']
    
    def mark_as_sent(self, request, queryset):
        """Mark invoices as sent"""
        updated = queryset.update(
            is_sent=True,
            sent_at=timezone.now()
        )
        self.message_user(request, f"Marked {updated} invoices as sent.")
    mark_as_sent.short_description = _('Mark as sent')
    
    def download_invoices(self, request, queryset):
        """Download invoices (placeholder for actual implementation)"""
        self.message_user(request, f"Download functionality for {queryset.count()} invoices to be implemented.")
    download_invoices.short_description = _('Download invoices')
