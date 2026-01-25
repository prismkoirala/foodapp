"""
Simplified views matching external API format
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from .models import Restaurant
from .serializers import RestaurantSerializer, RestaurantListSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def restaurant_list(request):
    """
    List all active restaurants.

    GET /api/restaurants/
    """
    restaurants = Restaurant.objects.filter(is_active=True).order_by('name')
    serializer = RestaurantListSerializer(restaurants, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def restaurant_detail(request, pk):
    """
    Retrieve restaurant details with full menu.

    GET /api/restaurants/{id}/

    Returns restaurant data with nested menu structure:
    - menu_groups (Food, Drinks, etc.)
      - categories (Starters, Main Course, etc.)
        - items (individual menu items)

    Includes CSRF token for form submissions.
    """
    restaurant = get_object_or_404(Restaurant, pk=pk, is_active=True)
    serializer = RestaurantSerializer(restaurant, context={'request': request})

    # Prepare response data
    response_data = serializer.data

    # Add CSRF token
    response_data['csrfHeaderName'] = 'X-CSRFTOKEN'
    response_data['csrfToken'] = get_token(request)

    return Response(response_data, status=status.HTTP_200_OK)
