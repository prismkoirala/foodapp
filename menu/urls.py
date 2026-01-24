# menu/urls.py (add to your app's urls.py)
from django.urls import path
from .views.api_views import (
    RestaurantDetail, MenuGroupList,
    MenuCategoryList, MenuItemList
)

urlpatterns = [
    path('restaurants/<int:pk>/', RestaurantDetail.as_view(), name='restaurant-detail'),
    path('menu-groups/', MenuGroupList.as_view(), name='menu-group-list'),
    path('menu-categories/', MenuCategoryList.as_view(), name='menu-category-list'),
    path('menu-items/', MenuItemList.as_view(), name='menu-item-list'),
]