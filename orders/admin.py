from django.contrib import admin
from .models import Table, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal', 'created_at']
    fields = ['menu_item', 'quantity', 'unit_price', 'subtotal', 'special_instructions']


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'restaurant', 'qr_code', 'is_active', 'capacity', 'created_at']
    list_filter = ['restaurant', 'is_active', 'created_at']
    search_fields = ['table_number', 'qr_code']
    readonly_fields = ['qr_code', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('restaurant', 'table_number', 'capacity', 'is_active')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'restaurant', 'table', 'status',
        'total_amount', 'customer_name', 'created_at'
    ]
    list_filter = ['status', 'restaurant', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_phone']
    readonly_fields = [
        'order_number', 'created_at', 'confirmed_at', 'prepared_at',
        'ready_at', 'served_at', 'completed_at', 'updated_at'
    ]
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'restaurant', 'table', 'status')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone')
        }),
        ('Order Details', {
            'fields': ('total_amount', 'special_instructions')
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'confirmed_at', 'prepared_at',
                'ready_at', 'served_at', 'completed_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity', 'unit_price', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'menu_item__name']
    readonly_fields = ['subtotal', 'created_at']
