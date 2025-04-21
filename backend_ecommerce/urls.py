# backend_ecommerce/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from products.views import ProductImageAPIView
from upload import views
from products.views import home
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from products.urls import api_urlpatterns, web_urlpatterns

# Cấu hình Swagger Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Ecommerce API",
        default_version='v1',
    ),
    public=True,
)

# Định nghĩa các URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns)),  # API endpoints
    path('', include(web_urlpatterns)),  # Web endpoints
    path('api/v1/upload/', views.UploadImageAPIView.as_view(), name='upload-image'),  # API upload hình ảnh
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
    path('api/v1/product/<slug:slug>/images/', ProductImageAPIView.as_view(), name='product-images'),  # API hình ảnh sản phẩm
    path('accounts/', include('django.contrib.auth.urls')),  # URL xác thực mặc định của Django
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # Trang đăng nhập
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),  # Đăng xuất
    path('register/', include('users.urls')),  # Trang đăng ký
    path('', include('products.urls')),  # Include URLs từ app products
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Phục vụ file media trong quá trình phát triển