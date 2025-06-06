"""
URL configuration for todolist project with new architecture.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from apps.shared.views import health_check

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v2 - New Clean Architecture
    path('api/v2/tasks/', include('apps.tasks.presentation.urls')),
    path('api/v2/users/', include('apps.users.presentation.urls')),
    path('api/v2/auth/', include('apps.authentication.presentation.urls')),
    
    # API v1 - For frontend compatibility
    path('api/v1/auth/', include('apps.authentication.presentation.urls')),
    path('api/v1/tasks/', include('apps.tasks.presentation.urls')),
    path('api/v1/users/', include('apps.users.presentation.urls')),
    
    # API v1 - Legacy (for backward compatibility) - Commented out for simplification
    # path('api/v1/', include('api.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)