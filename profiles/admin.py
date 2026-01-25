from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


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
        'role',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'date_joined',
    )

    # Make these clickable to go to detail view
    list_display_links = ('get_identifier',)

    # Filters on the right side
    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
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
    ordering = ('-date_joined',)

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