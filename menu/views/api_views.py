# menu/views.py
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from menu.models import Restaurant, MenuGroup, MenuCategory, MenuItem
from menu.serializers import (
    RestaurantSerializer, MenuGroupSerializer,
    MenuCategorySerializer, MenuItemSerializer
)

class RestaurantDetail(generics.RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class MenuGroupList(generics.ListAPIView):
    queryset = MenuGroup.objects.all()
    serializer_class = MenuGroupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['restaurant']

class MenuCategoryList(generics.ListAPIView):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['menu_group']

class MenuItemList(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']  # For the search functionality across items