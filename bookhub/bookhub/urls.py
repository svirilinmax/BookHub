from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.http import JsonResponse


# Простой view для корневого URL
def api_root(request):
    return JsonResponse({
        'message': 'Welcome to BookHub API',
        'version': 'v1',
        'endpoints': {
            'authentication': '/api/auth/',
            'products': '/api/products/',
            'orders': '/api/orders/',
            'users': '/api/users/',
            'admin': '/admin/',
            'swagger': '/swagger/',
            'redoc': '/redoc/'
        }
    })


schema_view = get_schema_view(
    openapi.Info(
        title="BookHub API",
        default_version="v1",
        description="BookHub - интернет-магазин книг с кастомной аутентификацией",
        contact=openapi.Contact(email="admin@bookhub.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Корневой URL
    path('', api_root, name='api-root'),

    # Админка
    path('admin/', admin.site.urls),
    path('api/admin/permissions/', include('apps.authorization.urls')),

    # Документация API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/auth/', include('apps.authentication.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/users/', include('apps.users.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
