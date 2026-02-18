from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, PromoPhoneNumber


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Custom admin interface for CustomUser model.
    """
    # Fields shown when viewing/editing a user
    fieldsets = (
        (None, {
            'fields': ('phone', 'email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('username', 'first_name', 'last_name')
        }),
        (_('Role & Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Restaurant Management'), {
            'fields': ('managed_restaurants',),
            'classes': ('collapse',),  # collapsed by default
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    # Fields shown when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'email', 'password1', 'password2', 'role', 'is_active', 'is_staff')
        }),
    )

    # List view columns
    list_display = (
        'get_identifier',
        'email',
        'role',
        'first_name',
        'last_name',
        'get_managed_restaurants',
        'is_active',
        'is_staff',
    )

    # Make these clickable to go to detail view
    list_display_links = ('get_identifier',)

    # Filters on the right side
    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    # Search fields (very useful)
    search_fields = (
        'phone',
        'email',
        'username',
        'first_name',
        'last_name',
    )

    # Ordering in list view
    ordering = ('-id',)  # Order by newest first (since we removed date_joined)

    # Show managed restaurants inline (nice for managers)
    filter_horizontal = ('managed_restaurants', 'groups', 'user_permissions')

    # Custom read-only fields for security/audit
    readonly_fields = ('last_login', 'date_joined')

    def get_identifier(self, obj):
        """
        Display phone or email (whichever is used for login)
        """
        if obj.phone:
            return obj.phone
        if obj.email:
            return obj.email
        if obj.username:
            return obj.username
        return f"User #{obj.id}"
    
    get_identifier.short_description = _('Login Identifier')
    get_identifier.admin_order_field = 'phone'  # sort by phone if possible

    def get_managed_restaurants(self, obj):
        """
        Display comma-separated list of managed restaurant names
        """
        restaurants = obj.managed_restaurants.all()
        if restaurants:
            return ', '.join([restaurant.name for restaurant in restaurants[:3]])  # Show max 3 restaurants
        return '-'
    get_managed_restaurants.short_description = _('Restaurants')

    def get_queryset(self, request):
        """
        Optimize query by prefetching related restaurants
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related('managed_restaurants')

    # Optional: customize form for better UX (e.g. required fields depending on role)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Example: make phone required for CUSTOMER role when creating/editing
        if obj and obj.role == 'CUSTOMER':
            form.base_fields['phone'].required = True
        if obj and obj.role in ('MANAGER', 'OWNER'):
            form.base_fields['email'].required = True
            
        return form


@admin.register(PromoPhoneNumber)
class PromoPhoneNumberAdmin(admin.ModelAdmin):
    """
    Admin interface for PromoPhoneNumber model
    """
    list_display = ('phone_number', 'restaurant', 'created_at', 'get_formatted_date')
    list_filter = ('restaurant', 'created_at')
    search_fields = ('phone_number', 'restaurant__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Phone Number Information', {
            'fields': ('phone_number', 'restaurant')
        }),
        ('Timestamp Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_formatted_date(self, obj):
        """Display formatted date for better readability"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    get_formatted_date.short_description = 'Date Added'
    
    def get_queryset(self, request):
        """Optimize query by selecting related restaurant"""
        return super().get_queryset(request).select_related('restaurant')
    
    # Optional: Add action to export phone numbers
    actions = ['export_phone_numbers']
    
    def export_phone_numbers(self, request, queryset):
        """Export selected phone numbers as CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="promo_phone_numbers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Phone Number', 'Restaurant', 'Date Added'])
        
        for obj in queryset:
            writer.writerow([obj.phone_number, obj.restaurant.name, obj.created_at.strftime('%Y-%m-%d %H:%M')])
        
        self.message_user(request, f"Exported {queryset.count()} phone numbers successfully.")
        return response
    
    export_phone_numbers.short_description = 'Export selected phone numbers'