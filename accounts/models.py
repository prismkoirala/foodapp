from django.db import models
from django.contrib.auth.models import User
from menu.models import Restaurant


class RestaurantUser(models.Model):
    """
    Links users to restaurants for multi-tenancy.
    Defines user roles within the system.
    """
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('RESTAURANT_MANAGER', 'Restaurant Manager'),
        ('KITCHEN_STAFF', 'Kitchen Staff'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='restaurant_user'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        help_text='Restaurant this user belongs to (null for super admins)'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='KITCHEN_STAFF'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurant_users'
        verbose_name = 'Restaurant User'
        verbose_name_plural = 'Restaurant Users'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['restaurant']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def is_super_admin(self):
        return self.role == 'SUPER_ADMIN'

    @property
    def is_restaurant_manager(self):
        return self.role in ['SUPER_ADMIN', 'RESTAURANT_MANAGER']

    @property
    def is_kitchen_staff(self):
        return self.role in ['SUPER_ADMIN', 'RESTAURANT_MANAGER', 'KITCHEN_STAFF']
