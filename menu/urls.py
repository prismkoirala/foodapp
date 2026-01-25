"""
Menu URLs matching external API format
"""
from django.urls import path
from . import views

urlpatterns = [
    # List all restaurants
    path('restaurants/', views.restaurant_list, name='restaurant-list'),

    # Get restaurant with full menu
    path('restaurants/<int:pk>/', views.restaurant_detail, name='restaurant-detail'),
]
