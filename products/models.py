from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')  # Thêm trường parent

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    amount = models.IntegerField()
    is_public = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='products/', blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    slug = models.SlugField(max_length=255, unique=True)
    is_flash_sale = models.BooleanField(default=False)
    flash_sale_end = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True)
    def __str__(self):
        return self.name

    def get_discounted_price(self):
        """Tính giá sau giảm giá dựa trên discount (phần trăm)."""
        if self.discount > 0:
            return self.price * (1 - self.discount / 100)
        return self.price

    class Meta:
        ordering = ['-created_at']

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class ProductComment(models.Model):
    rating = models.IntegerField()
    comment = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def get_total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order {self.order.id}"

class FavoriteProduct(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
class News(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=255)  # Có thể thay bằng slug nếu bạn dùng slug
    created_at = models.DateTimeField(default=timezone.now)
    id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True, null=True)  # Thêm trường description
    image = models.ImageField(upload_to='news_images/', null=True, blank=True)  # Thêm trường image
    thumbnail = models.ImageField(upload_to='news_thumbnails/', null=True, blank=True)  # Thêm trường thumbnail
    deleted_at = models.DateTimeField(null=True, blank=True)  # Thêm trường deleted_at

    def __str__(self):
        return self.title

