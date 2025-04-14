from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductComment, Cart, CartItem, Order, OrderItem
import logging

class ProductImageSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        logger = logging.getLogger(__name__)
        logger.info(f"Received data for ProductImageSerializer: {data}")
        return super().to_internal_value(data)

    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'product': {'required': False}  # Không yêu cầu product trong dữ liệu gửi lên
        }
class ProductCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = ['id', 'rating', 'comment', 'product', 'user', 'created_at', 'updated_at', 'deleted_at']
        extra_kwargs = {
            'product': {'required': False},  # Không bắt buộc trong request
            'user': {'required': False}      # Không bắt buộc trong request
        }

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    comments = ProductCommentSerializer(many=True, read_only=True)
    category = 'CategorySerializer'
    class Meta:
        model = Product
        fields = ('id', 'name', 'unit', 'price', 'discount', 'amount', 'is_public', 'thumbnail', 'images', 'comments', 'category', 'slug', 'created_at', 'updated_at', 'deleted_at')

class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'products', 'created_at', 'updated_at', 'deleted_at')

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'created_at', 'updated_at')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'created_at', 'updated_at')

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ('id', 'user', 'total_price', 'status', 'items', 'created_at', 'updated_at')