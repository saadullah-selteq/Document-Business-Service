from django.contrib import admin
from django.urls import path, re_path
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Plexaar Document Service",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny,],
    url='http://127.0.0.1:8000/document_svc/pb/swagger/'  # Changed to local URL
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('document_svc/', include('documentService.urls')),
    path('document_svc/pb/Business/', include('documentBusinessService.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.with_ui(cache_timeout=0), name='schema-json'),
    path('document_svc/pb/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
