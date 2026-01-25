from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now as django_now


class Restaurant(models.Model):
    # Basic Information
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to='restaurants/', blank=True, null=True)

    # New Fields
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text='URL-friendly identifier')
    is_active = models.BooleanField(default=True, help_text='Enable/disable restaurant')
    business_hours = models.JSONField(
        default=dict,
        blank=True,
        help_text='Operating hours in JSON format'
    )
    timezone = models.CharField(max_length=50, default='UTC', help_text='Restaurant timezone')

    # Timestamps
    created_at = models.DateTimeField(default=django_now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class MenuGroup(models.Model):
    type = models.CharField(max_length=100)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_groups')
    group_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['group_order']

    def __str__(self):
        return f"{self.type} ({self.restaurant.name})"

class MenuCategory(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    menu_group = models.ForeignKey(MenuGroup, on_delete=models.CASCADE, related_name='categories')
    cat_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['cat_order']

    def __str__(self):
        return f"{self.name} ({self.menu_group.type} - {self.menu_group.restaurant.name})"

class MenuItem(models.Model):
    # Basic Information
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    item_order = models.PositiveIntegerField(default=0)

    # New Fields
    is_available = models.BooleanField(default=True, help_text='Toggle item availability')
    is_special_of_day = models.BooleanField(default=False, help_text='Mark as daily special')
    preparation_time = models.PositiveIntegerField(
        default=15,
        help_text='Estimated preparation time in minutes'
    )
    allergens = models.JSONField(
        default=list,
        blank=True,
        help_text='List of allergens (e.g., ["nuts", "dairy"])'
    )
    dietary_tags = models.JSONField(
        default=list,
        blank=True,
        help_text='Dietary tags (e.g., ["vegan", "gluten-free"])'
    )

    # Timestamps
    created_at = models.DateTimeField(default=django_now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['item_order']
        indexes = [
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['is_special_of_day']),
        ]

    def __str__(self):
        return self.name

    @property
    def restaurant(self):
        """Get the restaurant through the category->menu_group relationship."""
        return self.category.menu_group.restaurant
