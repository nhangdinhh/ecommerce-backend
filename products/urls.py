# products/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'product', views.ProductViewSet)
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'order', views.OrderViewSet, basename='order')

# API URLs
api_urlpatterns = [
    path('', include(router.urls)),
    path('category/<str:id_slug>/', views.CategoryDetailAPIView.as_view(), name='category-detail'),
    path('product/<str:slug>/images/', views.ProductImageAPIView.as_view(), name='product-image-list'),
    path('product/<str:slug>/images/<int:image_id>/', views.ProductImageAPIView.as_view(), name='product-image-detail'),
    path('product/<str:slug>/comments/', views.ProductCommentAPIView.as_view(), name='product-comment-list'),
    path('product/<str:slug>/comments/<int:comment_id>/', views.ProductCommentAPIView.as_view(), name='product-comment-detail'),
    path('get-csrf-token/', views.get_csrf_token, name='get-csrf-token'),
]

# Web URLs
web_urlpatterns = [
    path('', views.home, name='home'),
    path('categories/', views.category_list, name='category_list'),
    path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart_view'),
    path('order/create/', views.create_order, name='create_order'),
    path('orders/', views.order_list, name='order_list'),
]