# reset_and_add_products.py
import os
import cloudinary
import cloudinary.uploader
from products.models import Product, Category
from django.core.files import File

# Đường dẫn đến thư mục chứa hình ảnh
BASE_IMAGE_PATH = "C:/django_projects/backend_ecommerce/media/products/"

# Bước 1: Xác nhận và xóa tất cả sản phẩm và danh mục hiện có
confirm = input("Bạn có chắc chắn muốn xóa tất cả sản phẩm và danh mục hiện có? (y/n): ")
if confirm.lower() != 'y':
    print("Hủy xóa dữ liệu.")
    exit()
Product.objects.all().delete()
Category.objects.all().delete()
print("Deleted all existing products and categories")

# Bước 2: Tạo danh mục mới
categories = [
    {"name": "Phụ kiện", "slug": "phu-kien"},
    {"name": "Thời trang", "slug": "thoi-trang"},
    {"name": "Đồ gia dụng", "slug": "do-gia-dung"},
    {"name": "Điện tử", "slug": "dien-tu"},
    {"name": "Đồ chơi", "slug": "do-choi"},
    {"name": "Mỹ phẩm", "slug": "my-pham"},
    {"name": "Đồ ăn uống", "slug": "do-an-uong"},
    {"name": "Khác", "slug": "khac"},
]

for cat in categories:
    Category.objects.create(name=cat["name"], slug=cat["slug"])
print("Created new categories")

# Bước 3: Thêm sản phẩm mới và gán hình ảnh
products = [
    {"name": "airpod", "price": 50.00, "unit": "cái", "amount": 40, "discount": 5.00, "slug": "airpod", "category": "phu-kien", "image_file": "airpod.jpg"},
    {"name": "ao_khoac", "price": 120.00, "unit": "cái", "amount": 50, "discount": 15.00, "slug": "ao-khoac", "category": "thoi-trang", "image_file": "ao_khoac.jpg"},
    {"name": "ao_thun", "price": 50.00, "unit": "cái", "amount": 100, "discount": 10.00, "slug": "ao-thun", "category": "thoi-trang", "image_file": "ao_thun.jpg"},
    {"name": "ban", "price": 150.00, "unit": "cái", "amount": 20, "discount": 15.00, "slug": "ban", "category": "do-gia-dung", "image_file": "ban.jpg"},
    {"name": "ban_phim", "price": 30.00, "unit": "cái", "amount": 50, "discount": 0.00, "slug": "ban-phim", "category": "dien-tu", "image_file": "ban_phim.jpg"},
    {"name": "bong_tai", "price": 10.00, "unit": "cặp", "amount": 100, "discount": 0.00, "slug": "bong-tai", "category": "phu-kien", "image_file": "bong_tai.jpg"},
    {"name": "but_chi", "price": 5.00, "unit": "cây", "amount": 200, "discount": 0.00, "slug": "but-chi", "category": "phu-kien", "image_file": "but_chi.jpg"},
    {"name": "chao", "price": 50.00, "unit": "cái", "amount": 20, "discount": 5.00, "slug": "chao", "category": "do-gia-dung", "image_file": "chao.jpg"},
    {"name": "chuot_may_tinh", "price": 20.00, "unit": "cái", "amount": 60, "discount": 0.00, "slug": "chuot-may-tinh", "category": "dien-tu", "image_file": "chuot_may_tinh.jpg"},
    {"name": "dao", "price": 15.00, "unit": "cái", "amount": 80, "discount": 0.00, "slug": "dao", "category": "khac", "image_file": "dao.jpg"},
    {"name": "den_hoc", "price": 200.00, "unit": "cái", "amount": 15, "discount": 10.00, "slug": "den-hoc", "category": "do-gia-dung", "image_file": "den_hoc.jpg"},
    {"name": "dep", "price": 15.00, "unit": "đôi", "amount": 100, "discount": 0.00, "slug": "dep", "category": "thoi-trang", "image_file": "dep.jpg"},
    {"name": "dien_thoai", "price": 1200.00, "unit": "cái", "amount": 10, "discount": 20.00, "slug": "dien-thoai", "category": "dien-tu", "image_file": "dien_thoai.jpg"},
    {"name": "do_choi_xep_go", "price": 35.00, "unit": "bộ", "amount": 50, "discount": 5.00, "slug": "do-choi-xep-go", "category": "do-choi", "image_file": "do_choi_xep_go.jpg"},
    {"name": "dong_ho_co", "price": 80.00, "unit": "cái", "amount": 30, "discount": 10.00, "slug": "dong-ho-co", "category": "phu-kien", "image_file": "dong_ho_co.jpg"},
    {"name": "dong_ho_thong_minh", "price": 150.00, "unit": "cái", "amount": 20, "discount": 15.00, "slug": "dong-ho-thong-minh", "category": "phu-kien", "image_file": "dong_ho_thong_minh.jpg"},
    {"name": "ghe_cong_thai_hoc", "price": 250.00, "unit": "cái", "amount": 10, "discount": 15.00, "slug": "ghe-cong-thai-hoc", "category": "do-gia-dung", "image_file": "ghe_cong_thai_hoc.jpg"},
    {"name": "giay_tay", "price": 90.00, "unit": "đôi", "amount": 40, "discount": 10.00, "slug": "giay-tay", "category": "thoi-trang", "image_file": "giay_tay.jpg"},
    {"name": "giay_the_thao", "price": 110.00, "unit": "đôi", "amount": 30, "discount": 10.00, "slug": "giay-the-thao", "category": "thoi-trang", "image_file": "giay_the_thao.jpg"},
    {"name": "goi", "price": 35.00, "unit": "đôi", "amount": 80, "discount": 5.00, "slug": "goi", "category": "thoi-trang", "image_file": "goi.jpg"},
    {"name": "hoa_qua_say", "price": 20.00, "unit": "gói", "amount": 100, "discount": 0.00, "slug": "hoa-qua-say", "category": "do-an-uong", "image_file": "hoa_qua_say.jpg"},
    {"name": "ipad", "price": 800.00, "unit": "cái", "amount": 10, "discount": 15.00, "slug": "ipad", "category": "dien-tu", "image_file": "ipad.jpg"},
    {"name": "ke_dep", "price": 100.00, "unit": "cái", "amount": 20, "discount": 5.00, "slug": "ke-dep", "category": "khac", "image_file": "ke_dep.jpg"},
    {"name": "kem_chong_nang", "price": 40.00, "unit": "hộp", "amount": 60, "discount": 5.00, "slug": "kem-chong-nang", "category": "my-pham", "image_file": "kem_chong_nang.jpg"},
    {"name": "keo", "price": 10.00, "unit": "gói", "amount": 150, "discount": 0.00, "slug": "keo", "category": "khac", "image_file": "keo.jpg"},
    {"name": "khan", "price": 25.00, "unit": "cái", "amount": 50, "discount": 0.00, "slug": "khan", "category": "khac", "image_file": "khan.jpg"},
    {"name": "kinh_mat", "price": 60.00, "unit": "cái", "amount": 40, "discount": 5.00, "slug": "kinh-mat", "category": "phu-kien", "image_file": "kinh_mat.jpg"},
    {"name": "lego", "price": 40.00, "unit": "bộ", "amount": 30, "discount": 5.00, "slug": "lego", "category": "do-choi", "image_file": "lego.jpg"},
    {"name": "loa", "price": 70.00, "unit": "cái", "amount": 25, "discount": 10.00, "slug": "loa", "category": "dien-tu", "image_file": "loa.jpg"},
    {"name": "may_cao_rau", "price": 45.00, "unit": "cái", "amount": 30, "discount": 5.00, "slug": "may-cao-rau", "category": "my-pham", "image_file": "may_cao_rau.jpg"},
    {"name": "may_say", "price": 55.00, "unit": "cái", "amount": 25, "discount": 5.00, "slug": "may-say", "category": "my-pham", "image_file": "may_say.jpg"},
    {"name": "may_uon_toc", "price": 60.00, "unit": "cái", "amount": 20, "discount": 5.00, "slug": "may-uon-toc", "category": "my-pham", "image_file": "may_uon_toc.jpg"},
    {"name": "nhan", "price": 15.00, "unit": "cái", "amount": 100, "discount": 0.00, "slug": "nhan", "category": "phu-kien", "image_file": "nhan.jpg"},
    {"name": "noi_com", "price": 80.00, "unit": "cái", "amount": 25, "discount": 10.00, "slug": "noi-com", "category": "do-gia-dung", "image_file": "noi_com.jpg"},
    {"name": "nuoc_hoa", "price": 100.00, "unit": "chai", "amount": 30, "discount": 10.00, "slug": "nuoc-hoa", "category": "my-pham", "image_file": "nuoc_hoa.jpg"},
    {"name": "nuoc_loc_dong_chai", "price": 15.00, "unit": "chai", "amount": 150, "discount": 5.00, "slug": "nuoc-loc-dong-chai", "category": "do-an-uong", "image_file": "nuoc_loc_dong_chai.jpg"},
    {"name": "nuoc_ngot_dong_chai", "price": 12.00, "unit": "chai", "amount": 120, "discount": 3.00, "slug": "nuoc-ngot-dong-chai", "category": "do-an-uong", "image_file": "nuoc_ngot_dong_chai.jpg"},
    {"name": "o_dien", "price": 20.00, "unit": "cái", "amount": 50, "discount": 0.00, "slug": "o-dien", "category": "do-gia-dung", "image_file": "o_dien.jpg"},
    {"name": "op_lung", "price": 10.00, "unit": "cái", "amount": 100, "discount": 0.00, "slug": "op-lung", "category": "khac", "image_file": "op_lung.jpg"},
    {"name": "quan_dai", "price": 70.00, "unit": "cái", "amount": 50, "discount": 10.00, "slug": "quan-dai", "category": "thoi-trang", "image_file": "quan_dai.jpg"},
    {"name": "quan_ngan", "price": 40.00, "unit": "cái", "amount": 60, "discount": 5.00, "slug": "quan-ngan", "category": "thoi-trang", "image_file": "quan_ngan.jpg"},
    {"name": "sac", "price": 15.00, "unit": "cái", "amount": 80, "discount": 0.00, "slug": "sac", "category": "phu-kien", "image_file": "sac.jpg"},
    {"name": "sac_du_phong", "price": 30.00, "unit": "cái", "amount": 40, "discount": 5.00, "slug": "sac-du-phong", "category": "phu-kien", "image_file": "sac_du_phong.jpg"},
    {"name": "sach", "price": 25.00, "unit": "cuốn", "amount": 50, "discount": 0.00, "slug": "sach", "category": "khac", "image_file": "sach.jpg"},
    {"name": "son_duong", "price": 25.00, "unit": "cây", "amount": 70, "discount": 0.00, "slug": "son-duong", "category": "my-pham", "image_file": "son_duong.jpg"},
    {"name": "tai_nghe", "price": 40.00, "unit": "cái", "amount": 40, "discount": 5.00, "slug": "tai-nghe", "category": "phu-kien", "image_file": "tai_nghe.jpg"},
    {"name": "tai_nghe_khong_day", "price": 60.00, "unit": "cái", "amount": 30, "discount": 5.00, "slug": "tai-nghe-khong-day", "category": "phu-kien", "image_file": "tai_nghe_khong_day.jpg"},
    {"name": "tui_xach", "price": 80.00, "unit": "cái", "amount": 30, "discount": 10.00, "slug": "tui-xach", "category": "thoi-trang", "image_file": "tui_xach.jpg"},
    {"name": "vien_sui", "price": 20.00, "unit": "gói", "amount": 100, "discount": 0.00, "slug": "vien-sui", "category": "phu-kien", "image_file": "vien_sui.jpg"},
    {"name": "vong_co", "price": 15.00, "unit": "cái", "amount": 80, "discount": 0.00, "slug": "vong-co", "category": "phu-kien", "image_file": "vong_co.jpg"},
    {"name": "vong_tay", "price": 12.00, "unit": "cái", "amount": 90, "discount": 0.00, "slug": "vong-tay", "category": "phu-kien", "image_file": "vong_tay.jpg"},
]

# Tạo sản phẩm mới và gán hình ảnh
for prod in products:
    try:
        # Lấy danh mục
        category = Category.objects.get(slug=prod["category"])
        
        # Tạo hoặc cập nhật sản phẩm
        product = Product.objects.filter(slug=prod["slug"]).first()
        if not product:
            product = Product.objects.create(
                name=prod["name"],
                price=prod["price"],
                unit=prod["unit"],
                amount=prod["amount"],
                is_public=True,
                discount=prod["discount"],
                category=category,
                slug=prod["slug"],
            )
        
        # Gán hình ảnh
        image_path = os.path.join(BASE_IMAGE_PATH, prod["image_file"])
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                # Tải lên Cloudinary trực tiếp để kiểm tra
                upload_result = cloudinary.uploader.upload(
                    image_file,
                    folder="products",
                    public_id=prod["image_file"].split('.')[0],
                    overwrite=True,
                    resource_type="image"
                )
                if upload_result.get("secure_url"):
                    print(f"Uploaded image for {prod['name']} to Cloudinary: {upload_result['secure_url']}")
                    # Gán URL từ Cloudinary vào sản phẩm
                    product.image = upload_result["public_id"] + ".jpg"
                    product.save()
                else:
                    print(f"Failed to upload image for {prod['name']} to Cloudinary")
        else:
            raise FileNotFoundError(f"Image file not found for {prod['name']}: {image_path}")
            
    except Exception as e:
        print(f"Error creating product {prod['name']}: {str(e)}")

# Kiểm tra lại sản phẩm
products = Product.objects.all()
for prod in products:
    print(f"ID: {prod.id}, Product: {prod.name}, Image: {prod.image.url if prod.image else 'No image'}")
    if prod.image:
        public_id = prod.image.url.split('/')[-2] + '/' + prod.image.url.split('/')[-1].split('.')[0]
        full_url = cloudinary.CloudinaryImage(public_id).build_url()
        print(f"Full Cloudinary URL: {full_url}")