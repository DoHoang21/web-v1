from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-2026')

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///shop.db')
# Fix PostgreSQL URL format for SQLAlchemy
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== MODELS ====================

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
    status = db.Column(db.String(20), default='pending')  # pending, paid, shipped, delivered
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


# ==================== ROUTES ====================

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=12)
    return render_template('index.html', products=products, title='Trang Chủ')


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            return render_template('register.html', error='Vui lòng điền đầy đủ thông tin')
        
        if password != confirm_password:
            return render_template('register.html', error='Mật khẩu không khớp')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Tên người dùng đã tồn tại')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email đã tồn tại')
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
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
        else:
            return render_template('login.html', error='Tên đăng nhập hoặc mật khẩu không đúng')
    
    return render_template('login.html', title='Đăng Nhập')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total_price=total_price, title='Giỏ Hàng')


@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    quantity = request.form.get('quantity', 1, type=int)
    product = Product.query.get_or_404(product_id)
    
    if product.quantity < quantity:
        return jsonify({'success': False, 'message': 'Số lượng sản phẩm không đủ'}), 400
    
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Thêm vào giỏ hàng thành công'})


@app.route('/remove-from-cart/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    cart_item = CartItem.query.get_or_404(cart_item_id)
    if cart_item.user_id != user_id:
        return jsonify({'success': False, 'message': 'Không có quyền xóa'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not cart_items:
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        
        order = Order(user_id=user_id, total_price=total_price, status='paid')
        db.session.add(order)
        db.session.flush()
        
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            cart_item.product.quantity -= cart_item.quantity
            db.session.add(order_item)
        
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return redirect(url_for('order_success', order_id=order.id))
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, 
                         user=user, title='Thanh Toán')


@app.route('/order-success/<int:order_id>')
def order_success(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    order = Order.query.get_or_404(order_id)
    if order.user_id != user_id:
        return jsonify({'success': False, 'message': 'Không có quyền xem'}), 403
    
    return render_template('order_success.html', order=order, title='Đơn Hàng Thành Công')


@app.route('/orders')
def orders():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    orders = Order.query.filter_by(user_id=user_id).all()
    return render_template('orders.html', orders=orders, title='Đơn Hàng Của Tôi')


@app.route('/admin')
def admin():
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return redirect(url_for('login'))
    
    products = Product.query.all()
    orders = Order.query.all()
    users = User.query.all()
    
    return render_template('admin.html', products=products, orders=orders, 
                         users=users, title='Trang Quản Trị')


@app.route('/admin/add-product', methods=['POST'])
def admin_add_product():
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    # Lấy dữ liệu từ form
    name = request.form.get('name')
    description = request.form.get('description')
    price_str = request.form.get('price')
    quantity_str = request.form.get('quantity')
    image_url = request.form.get('image_url', '')
    
    # Validate required fields
    if not name:
        flash('Tên sản phẩm không được để trống', 'error')
        return redirect(url_for('admin'))
    
    if not price_str:
        flash('Giá sản phẩm không được để trống', 'error')
        return redirect(url_for('admin'))
    
    if not quantity_str:
        flash('Số lượng sản phẩm không được để trống', 'error')
        return redirect(url_for('admin'))
    
    try:
        price = float(price_str)
        quantity = int(quantity_str)
    except (ValueError, TypeError):
        flash('Giá và số lượng phải là số hợp lệ', 'error')
        return redirect(url_for('admin'))
    
    if price < 0:
        flash('Giá sản phẩm không được âm', 'error')
        return redirect(url_for('admin'))
    
    if quantity < 0:
        flash('Số lượng sản phẩm không được âm', 'error')
        return redirect(url_for('admin'))
    
    try:
        product = Product(
            name=name, 
            description=description, 
            price=price, 
            quantity=quantity, 
            image_url=image_url
        )
        db.session.add(product)
        db.session.commit()
        logger.info(f"Admin added product: {product.name} (id={product.id})")
        
        flash('Thêm sản phẩm thành công', 'success')
        return redirect(url_for('admin'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding product: {str(e)}")
        flash(f'Có lỗi xảy ra khi thêm sản phẩm: {str(e)}', 'error')
        return redirect(url_for('admin'))


@app.route('/admin/edit-product/<int:product_id>', methods=['POST'])
def admin_edit_product(product_id):
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    product = Product.query.get_or_404(product_id)
    product.name = request.form.get('name', product.name)
    product.description = request.form.get('description', product.description)
    product.price = request.form.get('price', product.price, type=float)
    product.quantity = request.form.get('quantity', product.quantity, type=int)
    product.image_url = request.form.get('image_url', product.image_url)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Cập nhật sản phẩm thành công'})


@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Xóa sản phẩm thành công'})


@app.route('/admin/update-order-status/<int:order_id>', methods=['POST'])
def admin_update_order_status(order_id):
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    order.status = status
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Cập nhật trạng thái đơn hàng thành công'})


# ==================== UTILS ====================

def init_db():
    """Khởi tạo cơ sở dữ liệu và thêm dữ liệu mẫu"""
    with app.app_context():
        db.create_all()
        
        # Tạo admin nếu chưa có
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@shop.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
        
        # Tạo các sản phẩm mẫu
        if Product.query.count() == 0:
            products = [
                Product(name='Laptop Dell', description='Laptop hiệu năng cao', 
                       price=15000000, quantity=10, image_url='/static/laptop.jpg'),
                Product(name='iPhone 14', description='Điện thoại thông minh', 
                       price=20000000, quantity=15, image_url='/static/iphone.jpg'),
                Product(name='AirPods Pro', description='Tai nghe không dây', 
                       price=4000000, quantity=20, image_url='/static/airpods.jpg'),
                Product(name='iPad Air', description='Máy tính bảng', 
                       price=16000000, quantity=8, image_url='/static/ipad.jpg'),
                Product(name='Apple Watch', description='Đồng hồ thông minh', 
                       price=8000000, quantity=12, image_url='/static/watch.jpg'),
                Product(name='MacBook Pro', description='Laptop chuyên nghiệp', 
                       price=25000000, quantity=5, image_url='/static/macbook.jpg'),
            ]
            for product in products:
                db.session.add(product)
        
        db.session.commit()


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404 Not Found: {request.path}")
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500 Internal Error: {str(e)}")
    db.session.rollback()
    return render_template('500.html'), 500


@app.before_request
def before_request():
    logger.info(f"Request: {request.method} {request.path}")


@app.after_request
def after_request(response):
    logger.info(f"Response: {response.status}")
    return response


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
