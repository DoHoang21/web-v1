from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import logging

# Cấu hình logging để theo dõi lỗi trên Render/Docker [cite: 3]
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-2026')

# Xử lý URL Database cho PostgreSQL 
database_url = os.environ.get('DATABASE_URL', 'sqlite:///shop.db')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== MODELS  ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='product', lazy=True, cascade='all, delete-orphan')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product', backref='cart_items')

# Đảm bảo bảng được tạo khi khởi chạy trong môi trường Docker/Gunicorn [cite: 3]
with app.app_context():
    db.create_all()

# ==================== ROUTES ====================

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=12)
    return render_template('index.html', products=products, title='Trang Chủ')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Mật khẩu không khớp', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại', 'error')
            return render_template('register.html')
        
        user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Đăng Ký')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('index'))
        flash('Sai tài khoản hoặc mật khẩu', 'error')
    return render_template('login.html', title='Đăng Nhập')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ==================== ADMIN ROUTES (Đã sửa chi tiết lỗi thêm sản phẩm) ====================

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    products = Product.query.all()
    orders = Order.query.all()
    users = User.query.all()
    return render_template('admin.html', products=products, orders=orders, users=users)

@app.route('/admin/add-product', methods=['POST'])
def admin_add_product():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    try:
        # 1. Lấy và làm sạch dữ liệu 
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price_str = request.form.get('price', '').strip()
        quantity_str = request.form.get('quantity', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        # 2. Kiểm tra trống
        if not name or not price_str or not quantity_str:
            flash('Vui lòng nhập đầy đủ Tên, Giá và Số lượng', 'error')
            return redirect(url_for('admin'))
        
        # 3. Ép kiểu an toàn (Sửa lỗi nhập ký tự lạ)
        try:
            price = float(price_str)
            quantity = int(quantity_str)
        except ValueError:
            flash('Giá và số lượng phải là số hợp lệ', 'error')
            return redirect(url_for('admin'))

        if price < 0 or quantity < 0:
            flash('Giá và số lượng không được là số âm', 'error')
            return redirect(url_for('admin'))
        
        # 4. Lưu vào Database
        product = Product(
            name=name, 
            description=description, 
            price=price, 
            quantity=quantity, 
            image_url=image_url if image_url else '/static/default.jpg'
        )
        db.session.add(product)
        db.session.commit()
        
        logger.info(f"Admin {session.get('username')} added product: {name}")
        flash('Thêm sản phẩm thành công!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding product: {str(e)}")
        flash(f'Lỗi hệ thống: {str(e)}', 'error')
        
    return redirect(url_for('admin'))

@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('is_admin'):
        return jsonify({'success': False}), 403
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Đã xóa sản phẩm', 'success')
    return redirect(url_for('admin'))

# ==================== KHỞI TẠO HỆ THỐNG ====================

if __name__ == '__main__':
    # Tạo admin mặc định nếu chưa có 
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@shop.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)