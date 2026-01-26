import os
from cloudinary_storage.storage import MediaCloudinaryStorage   
from django.db import models

def restaurant_logo_path(instance, filename):
    """
    Rename logo to: restaurants/<restaurant_name>.<ext>
    """
    ext = os.path.splitext(filename)[1].lower()  # .jpg, .png, etc.
    # Use .slugify if you want safe URL-friendly names (recommended)
    from django.utils.text import slugify
    clean_name = slugify(instance.name)  # "McDonald's" → "mcdonalds"
    return f"restaurants/{slugify(instance.name)}_{instance.pk or 'new'}{ext}"

def menu_category_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    from django.utils.text import slugify
    # You can include restaurant name too if you want hierarchy
    restaurant_slug = slugify(instance.menu_group.restaurant.name)
    category_slug = slugify(instance.name)
    return f"categories/{restaurant_slug}/{category_slug}{ext}"

def menu_item_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    from django.utils.text import slugify
    restaurant_slug = slugify(instance.category.menu_group.restaurant.name)
    category_slug = slugify(instance.category.name)
    item_slug = slugify(instance.name)
    menu_group = slugify(instance.category.menu_group.type)
    return f"items/{restaurant_slug}/{menu_group}/{category_slug}/{item_slug}{ext}"

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(
            upload_to=restaurant_logo_path, 
            blank=True,
            null=True,
            storage=MediaCloudinaryStorage()  
        )
    facebook_url = models.CharField(max_length=200, blank=True)
    instagram_url = models.CharField(max_length=200, blank=True)
    tiktok_url = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

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
    image = models.ImageField(
        upload_to=menu_category_path,
        blank=True,
        null=True,
        storage=MediaCloudinaryStorage()
    )
    menu_group = models.ForeignKey(MenuGroup, on_delete=models.CASCADE, related_name='categories')
    cat_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['cat_order']

    def __str__(self):
        return f"{self.name} ({self.menu_group.type} - {self.menu_group.restaurant.name})"

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to=menu_item_path,
        blank=True,
        null=True,
        storage=MediaCloudinaryStorage()
    )
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    item_order = models.PositiveIntegerField(default=0)
    is_disabled = models.BooleanField(default=False)

    class Meta:
        ordering = ['item_order']

    def __str__(self):
        return self.name
