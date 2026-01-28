# utils/admin.py
from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'restaurant',
        'is_active',
        'start_date',
        'end_date',
        'created_at',
    )
    list_filter = (
        'restaurant',
        'is_active',
        'start_date',
        'end_date',
    )
    search_fields = (
        'title',
        'message',
        'restaurant__name',
    )
    list_per_page = 20
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': (
                'restaurant',
                'title',
                'message',
            )
        }),
        ('Schedule & Status', {
            'fields': (
                'start_date',
                'end_date',
                'is_active',
            ),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Optional: show only active or recent ones by default
        return qs.order_by('-created_at')