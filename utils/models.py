from django.db import models

# Create your models here.
# utils/models.py
from django.db import models
from django.utils.text import slugify
import os
from cloudinary_storage.storage import MediaCloudinaryStorage


class Announcement(models.Model):
    restaurant = models.ForeignKey(
        'menu.Restaurant',  
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    title = models.CharField(max_length=200)  
    message = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Announcements"

    def __str__(self):
        return f"{self.title} - {self.restaurant.name}"

    @property
    def is_current(self):
        from datetime import date
        today = date.today()
        return self.is_active and (
            (self.start_date is None or self.start_date <= today) and
            (self.end_date is None or self.end_date >= today)
        )