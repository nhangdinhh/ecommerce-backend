from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product, ProductImage, ProductComment, Cart, CartItem, Order, OrderItem
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, ProductCommentSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
import cloudinary.uploader
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Category, Product, Cart, CartItem, Order
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    # Thêm logic để chỉ hiển thị giỏ hàng của user hiện tại
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    
@api_view(['GET'])
def custom_api_root(request, format=None):
    return Response({
        'category': request.build_absolute_uri('category/'),
        'product': request.build_absolute_uri('product/'),
        'cart': request.build_absolute_uri('cart/'),
        'order': request.build_absolute_uri('order/'),
    })

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
        logger = logging.getLogger(__name__)
        try:
            logger.info(f"Received request to upload image for product with slug: {slug}")
            product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
            logger.info(f"Product found: {product.name} (slug: {product.slug})")
            
            serializer = ProductImageSerializer(data=request.data)
            if serializer.is_valid():
                logger.info("Serializer is valid, proceeding to save image")
                serializer.save(product=product)
                logger.info(f"Image saved successfully: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Serializer validation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            logger.error(f"Product with slug {slug} not found")
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error while uploading image: {str(e)}", exc_info=True)
            return Response({"error": f"Failed to upload image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    def get(self, request, slug, id):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        image = get_object_or_404(ProductImage, id=id, product=product, deleted_at__isnull=True)
        serializer = ProductImageSerializer(image)
        return Response(serializer.data)

    def put(self, request, slug, id):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        image = get_object_or_404(ProductImage, id=id, product=product, deleted_at__isnull=True)
        serializer = ProductImageSerializer(image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, id):
        product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
        image = get_object_or_404(ProductImage, id=id, product=product, deleted_at__isnull=True)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
            serializer.save(product=product)
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
            comment = ProductComment.objects.get(id=id_slug, product=product, deleted_at__isnull=True)
            serializer = ProductCommentSerializer(comment)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except ProductComment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, product_id_slug, id_slug):
        try:
            product = Product.objects.get(slug=product_id_slug, deleted_at__isnull=True)
            comment = ProductComment.objects.get(id=id_slug, product=product, deleted_at__isnull=True)
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
            comment = ProductComment.objects.get(id=id_slug, product=product, deleted_at__isnull=True)
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
            cart.items.all().delete()
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

            cart.items.all().delete()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)



@ensure_csrf_cookie
def get_csrf_token(request):
    return HttpResponse("CSRF token set")

def home(request):
    return render(request, 'home.html')

# Danh sách danh mục và tạo danh mục
def category_list(request):
    categories = Category.objects.filter(deleted_at__isnull=True)
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        try:
            Category.objects.create(name=name, slug=slug)
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
        except Exception as e:
            messages.error(request, f'Error creating category: {str(e)}')
    return render(request, 'category_list.html', {'categories': categories})

# Danh sách sản phẩm và tạo sản phẩm
@login_required
def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    if request.method == 'POST':
        # Xử lý tạo sản phẩm mới
        if 'name' in request.POST:
            name = request.POST.get('name')
            unit = request.POST.get('unit')
            price = request.POST.get('price')
            discount = request.POST.get('discount', 0)
            amount = request.POST.get('amount')
            is_public = request.POST.get('is_public') == 'true'
            thumbnail = request.POST.get('thumbnail')
            category_id = request.POST.get('category')
            slug = request.POST.get('slug')

            try:
                category = Category.objects.get(id=category_id)
                Product.objects.create(
                    name=name,
                    unit=unit,
                    price=price,
                    discount=discount,
                    amount=amount,
                    is_public=is_public,
                    thumbnail=thumbnail,
                    category=category,
                    slug=slug
                )
                messages.success(request, f"Product '{name}' created successfully!")
            except Exception as e:
                messages.error(request, f"Error creating product: {str(e)}")
            return redirect('product_list')

        # Xử lý thêm vào giỏ hàng
        elif 'product_id' in request.POST:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            try:
                product = Product.objects.get(id=product_id)
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
                if not item_created:
                    cart_item.quantity += quantity
                    cart_item.save()
                else:
                    cart_item.quantity = quantity
                    cart_item.save()
                messages.success(request, f"Added {quantity} {product.name}(s) to cart!")
            except Exception as e:
                messages.error(request, f"Error adding to cart: {str(e)}")
            return redirect('product_list')

    return render(request, 'product_list.html', {'products': products, 'categories': categories})

@login_required
def cart_view(request):
    # Lấy giỏ hàng của user hiện tại
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_total = sum(item.get_total_price() for item in cart_items)

    if request.method == 'POST':
        if 'cart_item_id' in request.POST:
            cart_item_id = request.POST.get('cart_item_id')

            # Cập nhật số lượng
            if 'update_quantity' in request.POST:
                quantity = int(request.POST.get('quantity', 1))
                try:
                    cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
                    cart_item.quantity = quantity
                    cart_item.save()
                    messages.success(request, f"Updated quantity for {cart_item.product.name}.")
                except Exception as e:
                    messages.error(request, f"Error updating quantity: {str(e)}")

            # Xóa sản phẩm khỏi giỏ hàng
            elif 'remove_item' in request.POST:
                try:
                    cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
                    product_name = cart_item.product.name
                    cart_item.delete()
                    messages.success(request, f"Removed {product_name} from cart.")
                except Exception as e:
                    messages.error(request, f"Error removing item: {str(e)}")

            return redirect('cart_view')

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })

@login_required
def create_order(request):
    cart = Cart.objects.get(user=request.user)
    if not cart.items.all():
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')
    
    order = Order.objects.create(user=request.user)
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
    cart.items.all().delete()
    messages.success(request, "Order created successfully!")
    return redirect('order_list')

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'order_list.html', {'orders': orders})