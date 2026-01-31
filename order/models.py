from django.db import models

from django.conf import settings
from django.db.models import DecimalField, ExpressionWrapper, F, Sum

from menu.models import MenuItem, Restaurant


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
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COOKING = 'cooking'
    STATUS_CHECKOUT = 'checkout'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = (
        (STATUS_CONFIRMED, 'confirmed'),
        (STATUS_COOKING, 'cooking'),
        (STATUS_CHECKOUT, 'checkout'),
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
        null=False,
        blank=False,
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
        default=STATUS_CONFIRMED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Order {self.pk} - {self.restaurant.name}"

    @property
    def total(self):
        total_expr = ExpressionWrapper(
            F('quantity') * F('unit_price'),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        agg = self.items.aggregate(total=Sum(total_expr))
        return agg['total'] or 0


class OrderItem(models.Model):
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

    class Meta:
        unique_together = ('order', 'menu_item')

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"
