# Tech Store - Nền Tảng Mua Bán Trực Tuyến 🛍️

Một nền tảng e-commerce hoàn chỉnh được xây dựng bằng **Flask**, **SQLAlchemy**, **HTML5**, **CSS3** và **JavaScript**.

## ✨ Chức Năng Chính

### 👤 Quản Lý Tài Khoản
- ✅ Đăng ký tài khoản mới
- ✅ Đăng nhập / Đăng xuất an toàn
- ✅ Quản lý thông tin cá nhân
- ✅ Lịch sử mua hàng

### 🛍️ Mua Sắm
- ✅ Danh sách sản phẩm (12 items/trang)
- ✅ Chi tiết sản phẩm (ảnh, mô tả, giá, số lượng)
- ✅ Giỏ hàng (thêm, xóa sản phẩm)
- ✅ Thanh toán linh hoạt (COD, Chuyển khoản, Thẻ tín dụng)
- ✅ Xác nhận đơn hàng tức thời

### 📦 Quản Lý Đơn Hàng
- ✅ Theo dõi trạng thái (Chờ Xác Nhận → Đã Thanh Toán → Đang Gửi → Đã Giao)
- ✅ Lịch sử đơn hàng chi tiết
- ✅ Kiểm tra thông tin từng sản phẩm

### 👨‍💼 Trang Quản Trị (Admin)
- ✅ **Quản Lý Sản Phẩm**: Thêm, Sửa, Xóa, Cập nhật giá & số lượng
- ✅ **Quản Lý Đơn Hàng**: Cập nhật trạng thái, xem chi tiết đơn hàng
- ✅ **Quản Lý Người Dùng**: Liệt kê tất cả người dùng, phân biệt Admin & User
- ✅ **Giao Diện Tab**: Chuyển đổi dễ dàng giữa các mục

## 🚀 Cài Đặt Nhanh

### Yêu Cầu
- Python 3.8+
- pip
- SQLite (mặc định) hoặc PostgreSQL

### 1️⃣ Cài Đặt Dependencies
```bash
cd c:\Users\MyPC\Desktop\Điện toán đám mây\web_v1
pip install -r requirements.txt
```

### 2️⃣ Chạy Ứng Dụng
```bash
python app.py
```
Mở trình duyệt và truy cập: **http://localhost:5000**

### 3️⃣ Đăng Nhập Admin
- **Username**: `admin`
- **Password**: `admin123`

## 🔐 Tài Khoản Test

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| User | user | user123 |

## 📁 Cấu Trúc Dự Án

```
web_v1/
├── app.py                  # Backend chính
├── requirements.txt        # Dependencies
├── README.md              # Hướng dẫn này
├── render.yaml            # Config deploy Render
├── Dockerfile             # Config Docker
├── static/
│   └── style.css          # CSS chính cho toàn ứng dụng
└── templates/
    ├── layout.html        # Template chính
    ├── index.html         # Trang chủ (danh sách sản phẩm)
    ├── product_detail.html # Chi tiết sản phẩm
    ├── login.html         # Đăng nhập
    ├── register.html      # Đăng ký
    ├── cart.html          # Giỏ hàng
    ├── checkout.html      # Thanh toán
    ├── order_success.html # Xác nhận đơn hàng
    ├── orders.html        # Lịch sử đơn hàng
    └── admin.html         # Trang quản trị
```

## 🎯 Các API Endpoint Chính

| Method | URL | Chức Năng |
|--------|-----|----------|
| GET | `/` | Trang chủ |
| GET | `/product/<id>` | Chi tiết sản phẩm |
| GET/POST | `/register` | Đăng ký |
| GET/POST | `/login` | Đăng nhập |
| GET | `/logout` | Đăng xuất |
| GET | `/cart` | Xem giỏ hàng |
| POST | `/add-to-cart/<id>` | Thêm vào giỏ |
| POST | `/remove-from-cart/<id>` | Xóa khỏi giỏ |
| GET/POST | `/checkout` | Thanh toán |
| GET | `/order-success/<id>` | Xác nhận đơn hàng |
| GET | `/orders` | Lịch sử đơn hàng |
| GET | `/admin` | Trang quản trị |
| POST | `/admin/add-product` | Thêm sản phẩm |
| POST | `/admin/update-product/<id>` | Cập nhật sản phẩm |
| POST | `/admin/delete-product/<id>` | Xóa sản phẩm |
| POST | `/admin/update-order-status/<id>` | Cập nhật trạng thái đơn hàng |
| GET | `/admin/order/<id>` | Xem chi tiết đơn hàng (API) |

## 🗄️ Cơ Sở Dữ Liệu

### User (Người Dùng)
- id, username, email, password, is_admin, created_at

### Product (Sản Phẩm)
- id, name, description, price, quantity, image_url, created_at

### Order (Đơn Hàng)
- id, user_id, total_price, status, created_at

### OrderItem (Chi Tiết Đơn Hàng)
- id, order_id, product_id, quantity, price

### CartItem (Giỏ Hàng)
- id, user_id, product_id, quantity

## 🎨 Tính Năng Giao Diện

- ✅ **Responsive Design**: Hỗ trợ Mobile, Tablet, Desktop
- ✅ **Modern UI**: Gradient backgrounds, smooth animations
- ✅ **Dark-Light Support**: Tối ưu một cho cả mode sáng
- ✅ **Form Validation**: Server-side & Client-side
- ✅ **Error Handling**: 404, 500 pages
- ✅ **Flash Messages**: Thông báo thành công/lỗi

## 🔧 Biến Môi Trường

```bash
# Tùy chọn (sẽ sử dụng mặc định nếu không thiết lập)
SECRET_KEY=your-secret-key         # Flask session key
DATABASE_URL=sqlite:///shop.db      # Database connection
FLASK_ENV=development               # development hoặc production
PORT=5000                           # Port để chạy server
```

## 📚 Công Nghệ Sử Dụng

- **Backend**: Flask 2.3.2, SQLAlchemy 3.0.5
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Security**: Werkzeug password hashing
- **Deployment**: Docker, Render, Gunicorn

## 🐛 Debugging

Nếu gặp lỗi:
1. Kiểm tra logs trong terminal
2. Xóa file `shop.db` để reset database
3. Đảm bảo Python 3.8+ được cài đặt
4. Chạy lại `pip install -r requirements.txt`

## 🌐 Deploy

### Deploy lên Render
```bash
git push # Render sẽ tự động build từ render.yaml
```

### Deploy lên Docker
```bash
docker build -t techstore .
docker run -p 5000:5000 techstore
```

## 📝 License
MIT License - Tự do sử dụng cho mục đích cá nhân & thương mại

## 👥 Hỗ Trợ
- Email: support@techstore.com
- Hotline: 1900-xxxx

### Bước 3: Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Chạy Ứng Dụng
```bash
python app.py
```

Truy cập ứng dụng tại: **http://localhost:5000**

## 📝 Tài Khoản Admin Mặc Định
- **Tên Đăng Nhập**: admin
- **Mật Khẩu**: admin123

## 📁 Cấu Trúc Dự Án
```
web_v1/
├── app.py                 # Ứng dụng chính
├── requirements.txt       # Dependencies
├── Dockerfile            # Docker configuration
├── .env                  # Biến môi trường
├── templates/            # HTML templates
│   ├── layout.html      # Giao diện chung
│   ├── index.html       # Trang chủ
│   ├── login.html       # Đăng nhập
│   ├── register.html    # Đăng ký
│   ├── product_detail.html  # Chi tiết sản phẩm
│   ├── cart.html        # Giỏ hàng
│   ├── checkout.html    # Thanh toán
│   ├── order_success.html   # Đơn hàng thành công
│   ├── orders.html      # Lịch sử đơn hàng
│   └── admin.html       # Trang quản trị
└── static/              # Tài nguyên tĩnh (CSS, JS, ảnh)
```

## 🗄️ Cơ Sở Dữ Liệu

### Models
1. **User** - Người dùng
2. **Product** - Sản phẩm
3. **Order** - Đơn hàng
4. **OrderItem** - Chi tiết đơn hàng
5. **CartItem** - Giỏ hàng

## 🐳 Docker

Để chạy ứng dụng trong Docker:

```bash
docker build -t tech-store .
docker run -p 5000:5000 tech-store
```

## 📞 Liên Hệ và Hỗ Trợ
- Email: support@techstore.com
- Hotline: 1900-xxxx

## 📄 Giấy Phép
MIT License - Tự do sử dụng và phân phối

---
**Phiên Bản**: 1.0.0  
**Ngày Cập Nhật**: Tháng 2, 2026
