from django.db import models

from django.conf import settings
from django.db.models import DecimalField, ExpressionWrapper, F, Sum

from menu.models import MenuItem, Restaurant

# Nepali date support
import logging
logger = logging.getLogger(__name__)

try:
    import nepali_datetime
    NEPALI_DATETIME_AVAILABLE = True
    logger.info("nepali-datetime package loaded successfully")
except ImportError:
    NEPALI_DATETIME_AVAILABLE = False
    logger.warning("nepali-datetime package not installed. Nepali date fields will not be auto-populated.")


class RestaurantTable(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='tables',
    )
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('restaurant', 'name')

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"


class Order(models.Model):
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = (
        (STATUS_IN_PROGRESS, 'in_progress'),
        (STATUS_COMPLETED, 'completed'),
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='orders',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_created',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_IN_PROGRESS,
    )
    
    # Final billed amount (populated when checkout is completed)
    final_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Final amount with VAT")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Nepali date fields for filtering (stored as strings for easy querying)
    nepali_date = models.CharField(max_length=20, blank=True, null=True, help_text="Nepali date in YYYY-MM-DD format")
    nepali_year = models.PositiveIntegerField(blank=True, null=True, help_text="Nepali year (e.g., 2081)")
    nepali_month = models.PositiveIntegerField(blank=True, null=True, help_text="Nepali month (1-12)")
    nepali_day = models.PositiveIntegerField(blank=True, null=True, help_text="Nepali day (1-32)")

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['nepali_date']),
            models.Index(fields=['nepali_year', 'nepali_month']),
        ]

    def __str__(self):
        return f"Order {self.pk} - {self.restaurant.name}"

    def save(self, *args, **kwargs):
        # Auto-populate Nepali date fields on save
        if NEPALI_DATETIME_AVAILABLE and not self.nepali_date:
            try:
                from datetime import datetime
                now = datetime.now()
                nepali_now = nepali_datetime.datetime.from_datetime_date(now.date())
                self.nepali_date = nepali_now.strftime('%Y-%m-%d')
                self.nepali_year = nepali_now.year
                self.nepali_month = nepali_now.month
                self.nepali_day = nepali_now.day
            except Exception as e:
                logger.error(f"Failed to set Nepali date fields: {e}")
        super().save(*args, **kwargs)

    @property
    def nepali_date_formatted(self):
        """Returns Nepali date in a readable format"""
        if self.nepali_date:
            return self.nepali_date
        if NEPALI_DATETIME_AVAILABLE and self.created_at:
            try:
                nepali_dt = nepali_datetime.datetime.from_datetime_date(self.created_at.date())
                return nepali_dt.strftime('%Y-%m-%d')
            except Exception:
                pass
        return None

    @property
    def total(self):
        total_expr = ExpressionWrapper(
            F('quantity') * F('unit_price'),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        agg = self.items.aggregate(total=Sum(total_expr))
        return agg['total'] or 0


class OrderItem(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PREPARING = 'preparing'
    STATUS_READY = 'ready'
    STATUS_SERVED = 'served'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'pending'),
        (STATUS_PREPARING, 'preparing'),
        (STATUS_READY, 'ready'),
        (STATUS_SERVED, 'served'),
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('order', 'menu_item')

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity} ({self.status})"
