import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_ecommerce.settings')
django.setup()

from products.models import Category, Product
# Thêm vào file add_data.py
from products.models import ProductImage

def add_sample_images():
    laptop = Product.objects.get(slug="laptop")
    ProductImage.objects.create(
        image_url="path/to/laptop-image1.jpg",
        product=laptop,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

if __name__ == "__main__":
    add_sample_data()
    add_sample_images()

# Thêm vào file add_data.py
from products.models import ProductComment
from django.contrib.auth.models import User

def add_sample_comments():
    laptop = Product.objects.get(slug="laptop")
    user = User.objects.first()  # Lấy user đầu tiên, hoặc tạo mới
    if not user:
        user = User.objects.create_user(username="testuser", password="testpass")
    ProductComment.objects.create(
        rating=5,
        comment="Great laptop!",
        product=laptop,
        user=user,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

if __name__ == "__main__":
    add_sample_data()
    add_sample_images()
    add_sample_comments()
    
def add_sample_data():
    category1 = Category.objects.create(
        name="Electronics",
        slug="electronics",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    category2 = Category.objects.create(
        name="Clothing",
        slug="clothing",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    Product.objects.create(
        name="Laptop",
        unit="pcs",
        price=1000,
        discount=0,
        amount=10,
        is_public=True,
        thumbnail="path/to/laptop.jpg",
        category=category1,
        slug="laptop",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    Product.objects.create(
        name="T-Shirt",
        unit="pcs",
        price=20,
        discount=0,
        amount=20,
        is_public=True,
        thumbnail="path/to/tshirt.jpg",
        category=category2,
        slug="t-shirt",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

if __name__ == "__main__":
    add_sample_data()