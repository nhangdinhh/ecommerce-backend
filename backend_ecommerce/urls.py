from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from products.views import get_csrf_token  # I
from products.views import ProductImageAPIView
from upload import views  # Import views từ app upload
from products.views import home  # Import view mới
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
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
    path('', include('products.urls')),
    path("api/v1/", include('products.urls')),
    path("api/v1/upload/", views.UploadImageAPIView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/product/<slug:slug>/images/', ProductImageAPIView.as_view(), name='product-images'),
    path('api/get-csrf-token/', get_csrf_token, name='get-csrf-token'),  # Thêm endpoint
    path('accounts/', include('django.contrib.auth.urls')),  # Thêm URL cho đăng nhập/đăng xuất
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)