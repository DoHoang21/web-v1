# Tech Store - Nền Tảng Mua Bán Trực Tuyến

Dự án web e-commerce hoàn chỉnh được xây dựng bằng **Flask**, **SQLAlchemy**, và **HTML/CSS**.

## ✨ Chức Năng Chính

### 👤 Quản Lý Tài Khoản
- ✅ Đăng ký tài khoản mới
- ✅ Đăng nhập / Đăng xuất
- ✅ Quản lý hồ sơ người dùng
- ✅ Lịch sử đơn hàng

### 🛍️ Mua Sắm
- ✅ Danh sách sản phẩm với phân trang
- ✅ Chi tiết sản phẩm chi tiết
- ✅ Giỏ hàng
- ✅ Thanh toán (COD, Chuyển khoản, Thẻ tín dụng)
- ✅ Xác nhận đơn hàng

### 📦 Quản Lý Đơn Hàng
- ✅ Theo dõi trạng thái đơn hàng
- ✅ Lịch sử mua hàng
- ✅ Hủy đơn hàng

### 👨‍💼 Trang Quản Trị (Admin)
- ✅ Quản lý sản phẩm (Thêm, Sửa, Xóa)
- ✅ Quản lý đơn hàng (Cập nhật trạng thái)
- ✅ Quản lý người dùng
- ✅ Xem thống kê

## 🚀 Cài Đặt và Chạy

### Yêu Cầu
- Python 3.8+
- pip

### Bước 1: Clone hoặc Tải Dự Án
```bash
cd c:\Users\MyPC\Desktop\Điện toán đám mây\web_v1
```

### Bước 2: Tạo Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

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
