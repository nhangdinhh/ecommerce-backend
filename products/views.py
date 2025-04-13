from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product, ProductImage, ProductComment, Cart, CartItem, Order, OrderItem
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, ProductCommentSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilte
def home(request):
    return HttpResponse("Welcome to the Ecommerce API! Available endpoints: /api/v1/category/, /api/v1/product/, /api/v1/cart/, /api/v1/order/")

# Category API Views
class CategoryAPIView(APIView):
    def get(self, request):
        categories = Category.objects.filter(deleted_at__isnull=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailAPIView(APIView):
    def get(self, request, id_slug):
        try:
            category = Category.objects.get(slug=id_slug, deleted_at__isnull=True)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id_slug):
        try:
            category = Category.objects.get(slug=id_slug, deleted_at__isnull=True)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id_slug):
        try:
            category = Category.objects.get(slug=id_slug, deleted_at__isnull=True)
            category.deleted_at = timezone.now()
            category.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

# Product API Views
class ProductAPIView(APIView):
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category']  # Lọc theo danh mục
    search_fields = ['name']  # Tìm kiếm theo tên

    def get(self, request, slug=None):
        if slug:
            product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        else:
            products = Product.objects.filter(deleted_at__isnull=True)

            # Áp dụng bộ lọc
            for backend in self.filter_backends:
                products = backend().filter_queryset(request, products, self)

            # Áp dụng phân trang
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(products, request)
            serializer = ProductSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

class ProductDetailAPIView(APIView):
    def get(self, request, id_slug):  # Sửa pk thành id_slug để đồng bộ với urls.py
        try:
            product = Product.objects.get(slug=id_slug, deleted_at__isnull=True)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id_slug):
        try:
            product = Product.objects.get(slug=id_slug, deleted_at__isnull=True)
            serializer = ProductSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id_slug):
        try:
            product = Product.objects.get(slug=id_slug, deleted_at__isnull=True)
            product.deleted_at = timezone.now()
            product.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

class ProductImageAPIView(APIView):
    def get(self, request, slug, image_id=None):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        if image_id:
            image = get_object_or_404(ProductImage, id=image_id, product=product, deleted_at__isnull=True)
            serializer = ProductImageSerializer(image)
        else:
            images = ProductImage.objects.filter(product=product, deleted_at__isnull=True)
            serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, slug, image_id):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        image = get_object_or_404(ProductImage, id=image_id, product=product, deleted_at__isnull=True)
        serializer = ProductImageSerializer(image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, image_id):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        image = get_object_or_404(ProductImage, id=image_id, product=product, deleted_at__isnull=True)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ProductImageDetailAPIView(APIView):
    def get(self, request, product_id_slug, id_slug):
        try:
            product = Product.objects.get(slug=product_id_slug, deleted_at__isnull=True)
            image = ProductImage.objects.get(id=id_slug, product=product, deleted_at__isnull=True)  # Sửa slug thành id
            serializer = ProductImageSerializer(image)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except ProductImage.DoesNotExist:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, product_id_slug, id_slug):
        try:
            product = Product.objects.get(slug=product_id_slug, deleted_at__isnull=True)
            image = ProductImage.objects.get(id=id_slug, product=product, deleted_at__isnull=True)  # Sửa slug thành id
            serializer = ProductImageSerializer(image, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except ProductImage.DoesNotExist:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, product_id_slug, id_slug):
        try:
            product = Product.objects.get(slug=product_id_slug, deleted_at__isnull=True)
            image = ProductImage.objects.get(id=id_slug, product=product, deleted_at__isnull=True)  # Sửa slug thành id
            image.deleted_at = timezone.now()
            image.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except ProductImage.DoesNotExist:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

# Product Comment API Views
class ProductCommentAPIView(APIView):
    pagination_class = PageNumberPagination

    def get(self, request, slug, comment_id=None):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        if comment_id:
            comment = get_object_or_404(ProductComment, id=comment_id, product=product, deleted_at__isnull=True)
            serializer = ProductCommentSerializer(comment)
            return Response(serializer.data)
        else:
            comments = ProductComment.objects.filter(product=product, deleted_at__isnull=True)
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(comments, request)
            serializer = ProductCommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        serializer = ProductCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, slug, comment_id):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        comment = get_object_or_404(ProductComment, id=comment_id, product=product, deleted_at__isnull=True)
        serializer = ProductCommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, comment_id):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        comment = get_object_or_404(ProductComment, id=comment_id, product=product, deleted_at__isnull=True)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ProductCommentDetailAPIView(APIView):
    def get(self, request, product_id_slug, id_slug):
        try:
            product = Product.objects.get(slug=product_id_slug, deleted_at__isnull=True)
            comment = ProductComment.objects.get(id=id_slug, product=product, deleted_at__isnull=True)  # Sửa slug thành id
            serializer = ProductCommentSerializer(comment)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except ProductComment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, product_id_slug, id_slug):
        try:
            product = Product.objects.get(slug=product_id_slug, deleted_at__isnull=True)
            comment = ProductComment.objects.get(id=id_slug, product=product, deleted_at__isnull=True)  # Sửa slug thành id
            serializer = ProductCommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except ProductComment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, product_id_slug, id_slug):
        try:
            product = Product.objects.get(slug=product_id_slug, deleted_at__isnull=True)
            comment = ProductComment.objects.get(id=id_slug, product=product, deleted_at__isnull=True)  # Sửa slug thành id
            comment.deleted_at = timezone.now()
            comment.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except ProductComment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

# Cart API Views
class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        try:
            product = Product.objects.get(id=product_id, deleted_at__isnull=True)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += int(quantity)
                cart_item.save()
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()  # Xóa tất cả CartItem trong giỏ hàng
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

# Order API Views
class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

            total_price = sum(item.product.price * item.quantity for item in cart.items.all())
            order = Order.objects.create(user=request.user, total_price=total_price)

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            cart.items.all().delete()  # Xóa giỏ hàng sau khi đặt hàng
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)