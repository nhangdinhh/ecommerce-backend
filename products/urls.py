from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Cấu hình router cho API ViewSets
router = DefaultRouter()
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'product', views.ProductViewSet, basename='product')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'order', views.OrderViewSet, basename='order')

app_name = 'products'

# URL patterns cho API
api_urlpatterns = [
    path('', views.custom_api_root, name='api-root'),  # API root
    path('', include(router.urls)),  # Các URL từ router (category, product, cart, order)
    path('category/', views.CategoryAPIView.as_view(), name='category_list_api'),
    path('category/<str:id_slug>/', views.CategoryDetailAPIView.as_view(), name='category_detail_api'),
    path('product/<slug:slug>/images/', views.ProductImageAPIView.as_view(), name='product_image_list'),
    path('product/<slug:slug>/images/<int:image_id>/', views.ProductImageAPIView.as_view(), name='product_image_detail'),
    path('product/<slug:slug>/images/<int:id>/', views.ProductImageDetailAPIView.as_view(), name='product_image_detail_alt'),
    path('product/<slug:slug>/comments/', views.ProductCommentAPIView.as_view(), name='product_comment_list'),
    path('product/<slug:slug>/comments/<int:comment_id>/', views.ProductCommentAPIView.as_view(), name='product_comment_detail'),
    path('product/<str:product_id_slug>/comments/<str:id_slug>/', views.ProductCommentDetailAPIView.as_view(), name='product_comment_detail_alt'),
    path('cart/', views.CartAPIView.as_view(), name='cart_api'),
    path('order/', views.OrderAPIView.as_view(), name='order_api'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]

# URL patterns cho giao diện web
web_urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),  # Sử dụng HomeView thay vì home
    path('category/', views.category_list, name='category_list'),  # Danh sách danh mục
    path('products/', views.product_list, name='product_list'),  # Danh sách sản phẩm
    path('cart/', views.cart_view, name='cart_view'),  # Giỏ hàng
    path('checkout/', views.checkout, name='checkout'),  # Thanh toán
    path('order-success/', views.order_success, name='order_success'),  # Trang thành công sau đặt hàng
    path('orders/', views.order_list, name='order_list'),  # Danh sách đơn hàng
    path('category/<int:id>/', views.CategoryProductsView.as_view(), name='category_products'),  # Sản phẩm theo danh mục
    path('search/', views.search_view, name='search'),  # Tìm kiếm
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),  # Chi tiết sản phẩm
    path('profile/', views.profile_view, name='profile'),  # Trang profile người dùng
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),  # Chi tiết tin tức
]

# Gộp api_urlpatterns và web_urlpatterns thành urlpatterns
urlpatterns = [
    path('api/', include(api_urlpatterns)),  # API URLs với prefix 'api/'
    path('', include(web_urlpatterns)),  # Web URLs không có prefix
]