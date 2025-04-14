# products/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'product', views.ProductViewSet)

urlpatterns = [
    path('category/', views.CategoryAPIView.as_view(), name='category-list'),
    path('category/<str:id_slug>/', views.CategoryDetailAPIView.as_view(), name='category-detail'),
    path('product/<str:slug>/images/', views.ProductImageAPIView.as_view(), name='product-image-list'),
    path('product/<str:slug>/images/<int:image_id>/', views.ProductImageAPIView.as_view(), name='product-image-detail'),
    path('product/<str:slug>/comments/', views.ProductCommentAPIView.as_view(), name='product-comment-list'),
    path('product/<str:slug>/comments/<int:comment_id>/', views.ProductCommentAPIView.as_view(), name='product-comment-detail'),
    path('cart/', views.CartAPIView.as_view(), name='cart'),
    path('order/', views.OrderAPIView.as_view(), name='order'),
    path('', include(router.urls)),
    path('get-csrf-token/', views.get_csrf_token, name='get-csrf-token'),
    path('', views.home, name='home'),
    path('categories/', views.category_list, name='category_list'),
    path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart_view'),
    path('order/create/', views.create_order, name='create_order'),
    path('orders/', views.order_list, name='order_list'),
]