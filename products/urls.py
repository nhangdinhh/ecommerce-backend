from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('get-csrf-token/', views.get_csrf_token, name='get-csrf-token'),
    path('category/', views.CategoryAPIView.as_view(), name='category-list'),
    path('category/<slug:id_slug>/', views.CategoryDetailAPIView.as_view(), name='category-detail'),
    path('product/<slug:slug>/images/', views.ProductImageAPIView.as_view(), name='product-image-list'),
    path('product/<slug:slug>/images/<int:id>/', views.ProductImageDetailAPIView.as_view(), name='product-image-detail'),
    path('product/<slug:slug>/comments/', views.ProductCommentAPIView.as_view(), name='product-comment-list'),
    path('product/<slug:product_id_slug>/comments/<str:id_slug>/', views.ProductCommentDetailAPIView.as_view(), name='product-comment-detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('order/create/', views.create_order, name='create_order'),
    path('orders/', views.order_list, name='order_list'),
    path('', views.home, name='home'),
    path('categories/', views.category_list, name='category_list'),
    path('products/', views.product_list, name='product_list'),
]
