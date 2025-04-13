from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from upload import views  # Import views từ app upload
from products.views import home  # Import view mới
from django.conf import settings
from django.conf.urls.static import static
schema_view = get_schema_view(
    openapi.Info(
        title="Ecommerce API",
        default_version='v1',
    ),
    public=True,
)

urlpatterns = [
    path('', home, name='home'),  # Route cho đường dẫn gốc
    path("admin/", admin.site.urls),
    path("api/v1/", include('products.urls')),
    path("api/v1/upload/", views.UploadImageAPIView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)