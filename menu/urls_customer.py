"""
URL patterns for customer-facing menu API endpoints.
"""
from django.urls import path
from .views.api_views import (
    RestaurantDetail,
    MenuGroupList,
    MenuCategoryList,
    MenuItemList
)

app_name = 'customer_menu'

urlpatterns = [
    # Customer menu browsing endpoints (read-only)
    path('restaurants/<int:pk>/', RestaurantDetail.as_view(), name='restaurant-detail'),
    path('restaurants/<slug:slug>/', RestaurantDetail.as_view(), name='restaurant-detail-by-slug'),
    path('menu-groups/', MenuGroupList.as_view(), name='menu-group-list'),
    path('menu-categories/', MenuCategoryList.as_view(), name='menu-category-list'),
    path('menu-items/', MenuItemList.as_view(), name='menu-item-list'),
]
