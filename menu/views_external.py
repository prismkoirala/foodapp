"""
Views matching the external API format from gipech.pythonanywhere.com
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from .models import Restaurant
from .serializers_external import ExternalRestaurantSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def external_restaurant_detail(request, pk):
    """
    Retrieve restaurant details with full menu in the external API format.

    Matches the structure from: http://gipech.pythonanywhere.com/api/restaurants/1/

    Returns:
        {
            "id": 1,
            "name": "Restaurant Name",
            "address": "Address",
            "phone": "Phone",
            "logo": "Full URL to logo",
            "menu_groups": [
                {
                    "id": 1,
                    "type": "Food",
                    "order": 0,
                    "categories": [
                        {
                            "id": 1,
                            "name": "Starters",
                            "order": 0,
                            "items": [
                                {
                                    "id": 1,
                                    "name": "Item Name",
                                    "price": "10.00",
                                    "order": 0,
                                    "description": "Description"
                                }
                            ]
                        }
                    ]
                }
            ],
            "csrfHeaderName": "X-CSRFTOKEN",
            "csrfToken": "..."
        }
    """
    restaurant = get_object_or_404(Restaurant, pk=pk, is_active=True)
    serializer = ExternalRestaurantSerializer(restaurant, context={'request': request})

    # Prepare response data
    response_data = serializer.data

    # Add CSRF token (like the external API)
    response_data['csrfHeaderName'] = 'X-CSRFTOKEN'
    response_data['csrfToken'] = get_token(request)

    return Response(response_data, status=status.HTTP_200_OK)
