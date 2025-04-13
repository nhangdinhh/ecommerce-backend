from django.urls import path
from . import views

urlpatterns = [
    path("category/", views.CategoryAPIView.as_view()),
    path("category/<slug:id_slug>/", views.CategoryDetailAPIView.as_view()),
    path("product/", views.ProductAPIView.as_view()),
    path("product/<slug:id_slug>/", views.ProductDetailAPIView.as_view()),
    path("product/<slug:product_id_slug>/images/", views.ProductImageAPIView.as_view()),
    path("product/<slug:product_id_slug>/images/<int:id_slug>/", views.ProductImageDetailAPIView.as_view()),  # Sửa slug thành int
    path("product/<slug:product_id_slug>/comments/", views.ProductCommentAPIView.as_view()),
    path("product/<slug:product_id_slug>/comments/<int:id_slug>/", views.ProductCommentDetailAPIView.as_view()),  # Sửa slug thành int
    path("cart/", views.CartAPIView.as_view(), name='cart'),
    path("order/", views.OrderAPIView.as_view(), name='order'),
]