"""
Root API views.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API Root - Welcome endpoint with links to all API sections.
    """
    return Response({
        'message': 'Welcome to the Restaurant Management API',
        'version': '1.0.0',
        'documentation': {
            'swagger_ui': request.build_absolute_uri(reverse('swagger-ui')),
            'openapi_schema': request.build_absolute_uri(reverse('schema')),
        },
        'endpoints': {
            'authentication': {
                'login': request.build_absolute_uri(reverse('accounts:login')),
                'logout': request.build_absolute_uri(reverse('accounts:logout')),
                'refresh_token': request.build_absolute_uri(reverse('accounts:token_refresh')),
                'current_user': request.build_absolute_uri(reverse('accounts:current_user')),
            },
            'manager_api': {
                'description': 'Restaurant management endpoints (authentication required)',
                'base_url': request.build_absolute_uri('/api/v1/manager/'),
                'endpoints': [
                    'restaurant/',
                    'menu-groups/',
                    'categories/',
                    'menu-items/',
                ]
            },
            'customer_api': {
                'description': 'Customer-facing menu browsing (public)',
                'base_url': request.build_absolute_uri('/api/v1/customer/menu/'),
                'endpoints': [
                    'restaurants/{id}/',
                    'restaurants/{slug}/',
                    'menu-groups/',
                    'menu-categories/',
                    'menu-items/',
                ]
            },
        },
        'admin_panel': request.build_absolute_uri('/admin/'),
    })
