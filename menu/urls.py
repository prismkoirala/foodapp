# menu/urls.py
from django.urls import path
from .views.api_views import (
    # Customer/Public views (for QR menu)
    RestaurantDetail, 
    MenuGroupList,
    MenuCategoryList, 
    MenuItemList, 
    HighlightedMenuItemsList,
    
    # Admin views (for restaurant management)
    RestaurantDetailAdmin,
    MenuGroupListAdmin,
    MenuCategoryListAdmin,
    MenuCategoryDetailAdmin,
    MenuItemListAdmin,
    MenuItemDetailAdmin,
    HighlightedMenuItemsListAdmin,
    
    # View menu count tracking
    increment_view_menu_count,
    
    # Bulk operations
    bulk_create_menu_items,
)

urlpatterns = [
    # ============================================
    # CUSTOMER/PUBLIC ENDPOINTS (Original - for QR menu)
    # No authentication required
    # ============================================
    path('restaurants/<int:pk>/', RestaurantDetail.as_view(), name='restaurant-detail'),
    path('restaurants/<int:restaurant_pk>/highlighted-items/', HighlightedMenuItemsList.as_view(), name='highlighted-items'),
    path('restaurants/<int:restaurant_pk>/increment-view-count/', increment_view_menu_count, name='increment-view-count'),
    path('menu-groups/', MenuGroupList.as_view(), name='menu-group-list'),
    path('menu-categories/', MenuCategoryList.as_view(), name='menu-category-list'),
    path('menu-items/', MenuItemList.as_view(), name='menu-item-list'),
    
    # ============================================
    # ADMIN ENDPOINTS (New - for restaurant management)
    # Requires authentication & filters by user's restaurant
    # ============================================
    path('admin/restaurants/<int:pk>/', RestaurantDetailAdmin.as_view(), name='admin-restaurant-detail'),
    path('admin/restaurants/<int:restaurant_pk>/highlighted-items/', HighlightedMenuItemsListAdmin.as_view(), name='admin-highlighted-items'),
    path('admin/menu-groups/', MenuGroupListAdmin.as_view(), name='admin-menu-group-list'),
    # Menu Categories - Full CRUD for admins
    path('admin/menu-categories/', MenuCategoryListAdmin.as_view(), name='admin-menu-category-list'),  # GET (list) + POST (create)
    path('admin/menu-categories/<int:pk>/', MenuCategoryDetailAdmin.as_view(), name='admin-menu-category-detail'),  # GET, PUT, PATCH, DELETE
    
    # Menu Items - Full CRUD for admins
    path('admin/menu-items/', MenuItemListAdmin.as_view(), name='admin-menu-item-list'),  # GET (list) + POST (create)
    path('admin/menu-items/<int:pk>/', MenuItemDetailAdmin.as_view(), name='admin-menu-item-detail'),  # GET, PUT, PATCH, DELETE
    
    # Bulk operations
    path('admin/menu-categories/<int:category_pk>/bulk-create-items/', bulk_create_menu_items, name='bulk-create-menu-items'),
]