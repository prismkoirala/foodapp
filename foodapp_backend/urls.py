"""
URL configuration - Simplified to match external API format
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import api_root

urlpatterns = [
    # Root API endpoint
    path('', api_root, name='api-root'),

    # Django Admin
    path("admin/", admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Main API
    path('api/', include([
        # Authentication
        path('auth/', include('accounts.urls')),

        # Menu endpoints (customer + manager)
        path('', include('menu.urls')),  # GET /api/restaurants/{id}/
        path('manager/', include('menu.urls_manager')),  # Manager menu management

        # Order endpoints (customer + kitchen + manager)
        path('', include('orders.urls')),  # All order endpoints
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
