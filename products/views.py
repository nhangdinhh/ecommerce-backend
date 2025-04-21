from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product, ProductImage, ProductComment, Cart, CartItem, Order, OrderItem, News
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, ProductCommentSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
import cloudinary.uploader
import logging
from datetime import timedelta
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from decimal import Decimal
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required


def home(request):
    categories = Category.objects.filter(parent__isnull=True, deleted_at__isnull=True)
    products = Product.objects.filter(deleted_at__isnull=True).select_related('category')

    products_list = list(products)
    flash_sale_products = random.sample(products_list, min(len(products_list), 4)) if products_list else []

    flash_sale_end = timezone.now() + timedelta(hours=24)

    # Lấy 5 tin tức mới nhất
    news_items = News.objects.filter(deleted_at__isnull=True).order_by('-created_at')[:5]

    context = {
        'categories': categories,
        'flash_sale_products': flash_sale_products,
        'products': products,
        'flash_sale_end': flash_sale_end,
        'news_items': news_items,
    }
    return render(request, 'home.html', context)
# View trang profile
@login_required
def profile_view(request):
    # Lấy thông tin người dùng
    user = request.user

    # Lấy lịch sử đơn hàng
    orders = Order.objects.filter(user=user).order_by('-created_at')

    # Lấy các đơn hàng đang chờ xử lý (giả sử trạng thái "Pending")
    pending_orders = orders.filter(status='Pending')

    # Giả sử có model FavoriteProduct để lưu sản phẩm yêu thích
    # Nếu chưa có, bạn có thể bỏ qua hoặc thêm model này
    try:
        favorite_products = Product.objects.filter(favoriteproduct__user=user)
    except:
        favorite_products = Product.objects.none()

    context = {
        'user': user,
        'orders': orders,
        'pending_orders': pending_orders,
        'favorite_products': favorite_products,
    }
    return render(request, 'profile.html', context)

# View trang chủ (class-based view)
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_public=True, deleted_at__isnull=True).select_related('category')  # Xóa [:8], thêm select_related
        context['categories'] = Category.objects.filter(parent=None, deleted_at__isnull=True)
        context['flash_sale_products'] = Product.objects.filter(is_flash_sale=True, is_public=True, deleted_at__isnull=True)[:4]
        context['flash_sale_end_time'] = Product.objects.filter(is_flash_sale=True, deleted_at__isnull=True).values_list('flash_sale_end', flat=True).first() or (timezone.now() + timedelta(hours=24))
        context['news_items'] = News.objects.filter(deleted_at__isnull=True).order_by('-created_at')[:5]
        print("News Items:", list(context['news_items']))
        return context
# View chi tiết tin tức
class NewsDetailView(DetailView):
    model = News
    template_name = 'news_detail.html'
    context_object_name = 'news'

    def get_queryset(self):
        return News.objects.filter(deleted_at__isnull=True)

# View chi tiết sản phẩm
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
    comments = product.product_comments.filter(deleted_at__isnull=True).order_by('-created_at').select_related('user')

    if request.method == 'POST':
        if 'add_to_cart' in request.POST:
            if not request.user.is_authenticated:
                messages.info(request, "Please log in to add items to your cart.")
                return redirect('login')

            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                messages.error(request, "Quantity must be at least 1.")
                return redirect('products:product_detail', slug=product.slug)

            # Kiểm tra số lượng tồn kho
            if product.amount < quantity:
                messages.error(request, f"Sorry, only {product.amount} {product.name}(s) left in stock.")
                return redirect('products:product_detail', slug=product.slug)

            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            # Cập nhật số lượng tồn kho
            product.amount -= quantity
            product.save()

            messages.success(request, f"Added {quantity} {product.name}(s) to cart!")
            return redirect('products:cart_view')

        elif 'add_comment' in request.POST:
            if not request.user.is_authenticated:
                messages.info(request, "Please log in to leave a review.")
                return redirect('login')

            rating = int(request.POST.get('rating', 0))
            comment_text = request.POST.get('comment', '').strip()

            if rating < 1 or rating > 5:
                messages.error(request, "Rating must be between 1 and 5.")
            elif not comment_text:
                messages.error(request, "Comment cannot be empty.")
            else:
                ProductComment.objects.create(
                    product=product,
                    user=request.user,
                    rating=rating,
                    comment=comment_text
                )
                messages.success(request, "Review submitted successfully!")
            return redirect('products:product_detail', slug=product.slug)

    context = {
        'product': product,
        'comments': comments,
    }
    return render(request, 'product_detail.html', context)

# View danh sách sản phẩm theo danh mục
class CategoryProductsView(ListView):
    template_name = 'category_products.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Lấy danh mục bằng id
        category = get_object_or_404(Category, id=self.kwargs['id'], deleted_at__isnull=True)
        
        # Hàm đệ quy để lấy tất cả danh mục con
        def get_all_subcategories(category):
            subcategories = [category]
            for subcategory in category.subcategories.filter(deleted_at__isnull=True):
                subcategories.extend(get_all_subcategories(subcategory))
            return subcategories

        # Lấy tất cả danh mục con (bao gồm cả con của con)
        all_categories = get_all_subcategories(category)
        category_ids = [cat.id for cat in all_categories]
        
        # Lấy sản phẩm thuộc danh mục hiện tại hoặc danh mục con
        return Product.objects.filter(category__id__in=category_ids, deleted_at__isnull=True).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, id=self.kwargs['id'], deleted_at__isnull=True)
        # Chỉ lấy danh mục con trực tiếp để hiển thị
        subcategories = category.subcategories.filter(deleted_at__isnull=True)
        context['category'] = category
        context['categories'] = subcategories  # Danh mục con
        return context

# View tìm kiếm sản phẩm
def search_view(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()  # Khởi tạo queryset rỗng

    if query:  # Chỉ tìm kiếm nếu query không rỗng
        products = Product.objects.filter(deleted_at__isnull=True).select_related('category').filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        # Kiểm tra số lượng sản phẩm khớp
        if products.count() == 1:  # Nếu chỉ có duy nhất 1 sản phẩm
            product = products.first()
            return redirect('products:product_detail', slug=product.slug)

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'search_results.html', context)

# View danh sách danh mục
def category_list(request):
    categories = Category.objects.filter(deleted_at__isnull=True)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        if not name or not slug:
            messages.error(request, "Name and slug are required.")
        else:
            try:
                Category.objects.create(name=name, slug=slug)
                messages.success(request, 'Category created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating category: {str(e)}')
        return redirect('products:category_list')
    return render(request, 'category_list.html', {'categories': categories})

# View danh sách sản phẩm
def product_list(request):
    products = Product.objects.filter(is_public=True, deleted_at__isnull=True).select_related('category')

    # Debug dữ liệu products
    print(f"Number of products: {products.count()}")
    for product in products:
        print(f"Product: {product.name}, Image: {product.image.url if product.image else 'No image'}")

    if request.method == 'POST':
        if 'product_id' in request.POST:
            if not request.user.is_authenticated:
                messages.info(request, "Please log in to add items to your cart.")
                return redirect('login')

            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))

            if quantity < 1:
                messages.error(request, "Quantity must be at least 1.")
                return redirect('products:product_list')

            try:
                product = Product.objects.get(id=product_id, deleted_at__isnull=True)

                if product.amount < quantity:
                    messages.error(request, f"Sorry, only {product.amount} {product.name}(s) left in stock.")
                    return redirect('products:product_list')

                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
                if not item_created:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = quantity
                cart_item.save()

                product.amount -= quantity
                product.save()

                messages.success(request, f"Added {quantity} {product.name}(s) to cart!")
            except Product.DoesNotExist:
                messages.error(request, "Product not found.")
            except Exception as e:
                messages.error(request, f"Error adding to cart: {str(e)}")
            return redirect('products:product_list')

    return render(request, 'product_list.html', {'products': products})

# View giỏ hàng
@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    cart_total = sum(item.get_total_price() for item in cart_items)

    if request.method == 'POST':
        if 'add_to_cart' in request.POST:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            try:
                product = Product.objects.get(id=product_id, deleted_at__isnull=True)
                if product.amount < quantity:
                    messages.error(request, f"Sorry, only {product.amount} {product.name}(s) left in stock.")
                    return redirect('products:cart_view')
                cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
                if not item_created:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = quantity
                cart_item.save()
                product.amount -= quantity
                product.save()
                messages.success(request, f"Added {quantity} {product.name}(s) to cart!")
            except Product.DoesNotExist:
                messages.error(request, "Product not found.")
            except Exception as e:
                messages.error(request, f"Error adding to cart: {str(e)}")
            return redirect('products:cart_view')

        if 'cart_item_id' in request.POST:
            cart_item_id = request.POST.get('cart_item_id')
            if 'update_quantity' in request.POST:
                quantity = int(request.POST.get('quantity', 1))
                try:
                    cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
                    if quantity < 1:
                        messages.error(request, "Quantity must be at least 1.")
                        return redirect('products:cart_view')
                    # Cập nhật lại số lượng tồn kho
                    old_quantity = cart_item.quantity
                    product = cart_item.product
                    product.amount += old_quantity  # Hoàn lại số lượng cũ
                    if product.amount < quantity:
                        messages.error(request, f"Sorry, only {product.amount} {product.name}(s) left in stock.")
                        product.amount -= old_quantity  # Khôi phục số lượng tồn kho
                        product.save()
                        return redirect('products:cart_view')
                    cart_item.quantity = quantity
                    cart_item.save()
                    product.amount -= quantity  # Trừ số lượng mới
                    product.save()
                    messages.success(request, f"Updated quantity for {cart_item.product.name}.")
                except CartItem.DoesNotExist:
                    messages.error(request, "Cart item not found.")
                except Exception as e:
                    messages.error(request, f"Error updating quantity: {str(e)}")
            elif 'remove_item' in request.POST:
                try:
                    cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
                    product = cart_item.product
                    product.amount += cart_item.quantity  # Hoàn lại số lượng tồn kho
                    product.save()
                    product_name = cart_item.product.name
                    cart_item.delete()
                    messages.success(request, f"Removed {product_name} from cart.")
                except CartItem.DoesNotExist:
                    messages.error(request, "Cart item not found.")
                except Exception as e:
                    messages.error(request, f"Error removing item: {str(e)}")
            return redirect('products:cart_view')

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })

# View thanh toán
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    cart_total = sum(item.get_total_price() for item in cart_items)

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('products:cart_view')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        address = request.POST.get('address', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        if not full_name or not address or not phone_number:
            messages.error(request, "Please fill in all shipping information.")
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'cart_total': cart_total,
            })

        order = Order.objects.create(
            user=request.user,
            total_price=cart_total,
            full_name=full_name,
            address=address,
            phone_number=phone_number
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        return redirect('products:order_success')

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })

# View xác nhận đặt hàng thành công
@login_required
def order_success(request):
    return render(request, 'order_success.html')

# View danh sách đơn hàng
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'order_list.html', {'orders': orders})

# API views
@api_view(['GET'])
def custom_api_root(request, format=None):
    return Response({
        'category': request.build_absolute_uri('category/'),
        'product': request.build_absolute_uri('product/'),
        'cart': request.build_absolute_uri('cart/'),
        'order': request.build_absolute_uri('order/'),
    })

# ViewSet cho Category
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(deleted_at__isnull=True)
    serializer_class = CategorySerializer

# ViewSet cho Product
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(deleted_at__isnull=True)
    serializer_class = ProductSerializer

# ViewSet cho Cart
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

# ViewSet cho Order
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

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

# Product Image API Views
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
            if product.amount < int(quantity):
                return Response({"error": f"Only {product.amount} {product.name}(s) left in stock."}, status=status.HTTP_400_BAD_REQUEST)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += int(quantity)
            else:
                cart_item.quantity = int(quantity)
            cart_item.save()
            product.amount -= int(quantity)
            product.save()
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            for item in cart.items.all():
                product = item.product
                product.amount += item.quantity  # Hoàn lại số lượng tồn kho
                product.save()
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
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

# CSRF Token
@ensure_csrf_cookie
def get_csrf_token(request):
    return HttpResponse("CSRF token set")




@login_required
def checkout_view(request):
    # Lấy giỏ hàng của user
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.get_total_price() for item in cart_items)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        shipping_method = request.POST.get('shipping_method')

        # Tính phí vận chuyển dựa trên phương thức
        shipping_fees = {
            'normal': 5.00,
            'fast': 10.00,
            'express': 20.00
        }
        shipping_fee = shipping_fees.get(shipping_method, 5.00)  # Mặc định là normal nếu không hợp lệ

        # Tạo đơn hàng
        order = Order.objects.create(
            user=request.user,
            total_price=cart_total,
            shipping_method=shipping_method,
            shipping_fee=shipping_fee
        )
        # Lưu thông tin giao hàng (có thể tạo model riêng hoặc lưu trực tiếp vào Order)
        order.full_name = full_name
        order.address = address
        order.phone_number = phone_number
        order.save()

        # Xóa giỏ hàng sau khi đặt hàng thành công
        cart_items.delete()

        return redirect('order_success')

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'checkout.html', context)