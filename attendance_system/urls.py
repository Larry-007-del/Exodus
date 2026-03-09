from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


@cache_control(max_age=86400, public=True)
def favicon_view(request):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" rx="6" fill="#4f46e5"/>'
        '<text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" '
        'fill="white" font-size="20" font-weight="bold">E</text></svg>'
    )
    return HttpResponse(svg, content_type='image/svg+xml')


urlpatterns = [
    # Favicon
    path('favicon.ico', favicon_view, name='favicon'),

    # Django Admin
    path('admin/', admin.site.urls),

    # Frontend URLs (including login/logout)
    path('', include('frontend.urls')),
    
    # API endpoints
    path('api/', include('attendance.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'frontend.views.error_404'
handler500 = 'frontend.views.error_500'
