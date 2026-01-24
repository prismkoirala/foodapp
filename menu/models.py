from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to='restaurants/', blank=True, null=True)

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
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
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
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    item_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['item_order']

    def __str__(self):
        return self.name
