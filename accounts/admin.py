from django.contrib import admin
from .models import RestaurantUser


@admin.register(RestaurantUser)
class RestaurantUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'restaurant', 'role')
        }),
        ('Contact', {
            'fields': ('phone_number',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
