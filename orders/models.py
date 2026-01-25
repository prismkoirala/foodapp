from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from menu.models import Restaurant, MenuItem
import secrets
from datetime import datetime


class Table(models.Model):
    """
    Represents a table in a restaurant with QR code for customer ordering.
    """
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='tables'
    )
    table_number = models.CharField(max_length=50, help_text='Table identifier (e.g., "Table 5", "Patio 3")')
    qr_code = models.CharField(max_length=100, unique=True, help_text='Unique QR code identifier')
    qr_code_image = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        help_text='Generated QR code image'
    )
    is_active = models.BooleanField(default=True)
    capacity = models.PositiveIntegerField(null=True, blank=True, help_text='Number of seats')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tables'
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        unique_together = [['restaurant', 'table_number']]
        indexes = [
            models.Index(fields=['restaurant', 'is_active']),
            models.Index(fields=['qr_code']),
        ]

    def __str__(self):
        return f"{self.table_number} - {self.restaurant.name}"

    def save(self, *args, **kwargs):
        # Generate QR code if not provided
        if not self.qr_code:
            self.qr_code = secrets.token_urlsafe(16)
        super().save(*args, **kwargs)


class Order(models.Model):
    """
    Represents a customer order.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready'),
        ('SERVED', 'Served'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=50, unique=True, help_text='Unique order identifier')
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        blank=True
    )

    # Customer Information (optional)
    customer_name = models.CharField(max_length=100, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)

    # Order Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    special_instructions = models.TextField(blank=True, help_text='Order-level special instructions')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    prepared_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['restaurant', 'status']),
            models.Index(fields=['restaurant', 'created_at']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.restaurant.name}"

    def save(self, *args, **kwargs):
        # Generate order number if not provided
        if not self.order_number:
            today = datetime.now().strftime('%Y%m%d')
            random_part = secrets.token_hex(4).upper()
            self.order_number = f"ORD-{today}-{random_part}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Represents individual items in an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    menu_item_snapshot = models.JSONField(
        help_text='Snapshot of menu item details at time of order'
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Price at time of order'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='quantity * unit_price'
    )
    special_instructions = models.TextField(blank=True, help_text='Item-specific special instructions')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['menu_item']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} - Order {self.order.order_number}"

    def save(self, *args, **kwargs):
        # Calculate subtotal
        self.subtotal = self.quantity * self.unit_price

        # Create menu item snapshot if not provided
        if not self.menu_item_snapshot:
            self.menu_item_snapshot = {
                'name': self.menu_item.name,
                'description': self.menu_item.description,
                'price': str(self.menu_item.price),
                'category': self.menu_item.category.name,
            }

        super().save(*args, **kwargs)
