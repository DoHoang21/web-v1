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

# ==================== UTILS (KHỞI TẠO DB) ====================

def init_db():
    """Khởi tạo cơ sở dữ liệu, admin và sản phẩm mẫu"""
    with app.app_context():
        db.create_all()
        
        # 1. Tạo admin nếu chưa có
        if not User.query.filter_by(username='admin').first():
            logger.info("Đang tạo tài khoản admin mặc định...")
            admin = User(
                username='admin',
                email='admin@shop.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            logger.info("Đã tạo Admin: admin / admin123")

        # 2. Thêm sản phẩm mẫu nếu database trống
        if Product.query.count() == 0:
            logger.info("Đang thêm sản phẩm mẫu vào cửa hàng...")
            sample_products = [
                Product(name='iPhone 15 Pro', description='Chip A17 Pro mạnh mẽ, khung Titan bền bỉ.', price=28990000, quantity=50, image_url='https://vcdn-sohoa.vnecdn.net/2023/09/13/iphone-15-pro-finish-select-202309-6x-9321-1694566311.jpg'),
                Product(name='MacBook Air M2', description='Siêu mỏng nhẹ, pin cả ngày dài.', price=26500000, quantity=30, image_url='https://vcdn-sohoa.vnecdn.net/2022/06/07/macbook-air-m2-1-8438-1654559865.jpg'),
                Product(name='iPad Pro M2', description='Màn hình Liquid Retina siêu sắc nét.', price=21990000, quantity=25, image_url='https://vcdn-sohoa.vnecdn.net/2022/10/19/ipad-pro-m2-1-8316-1666113941.jpg'),
                Product(name='Sony WH-1000XM5', description='Tai nghe chống ồn đỉnh cao.', price=8490000, quantity=40, image_url='https://sony.scene7.com/is/image/sonyglobalsolutions/wh-1000xm5_b_primary?fmt=png-alpha'),
                Product(name='Samsung Galaxy S24 Ultra', description='Điện thoại AI đỉnh nhất hiện nay.', price=29990000, quantity=20, image_url='https://vcdn-sohoa.vnecdn.net/2024/01/18/galaxy-s24-ultra-1-8931-1705520846.jpg'),
                Product(name='Apple Watch Series 9', description='Theo dõi sức khỏe và thể thao chuyên nghiệp.', price=10200000, quantity=15, image_url='https://vcdn-sohoa.vnecdn.net/2023/09/13/watch-series-9-1-5847-1694565755.jpg'),
                Product(name='Logitech MX Master 3S', description='Chuột công thái học cho dân văn phòng.', price=2450000, quantity=100, image_url='https://resource.logitech.com/w_692,c_lpad,ar_4:3,q_auto,f_auto,dpr_1.0/d_transparent.gif/content/dam/logitech/en/products/mice/mx-master-3s/gallery/mx-master-3s-mouse-top-view-graphite.png?v=1'),
                Product(name='Keychron K2 V2', description='Bàn phím cơ không dây nhỏ gọn.', price=1850000, quantity=60, image_url='https://product.hstatic.net/1000300271/product/k2_a_1_621b4a03780544f895c0c978b7e289c0.jpg')
            ]
            db.session.bulk_save_objects(sample_products)
            logger.info("Đã thêm 8 sản phẩm mẫu thành công!")
        
        db.session.commit()

# GỌI NGAY TẠI ĐÂY: Để Gunicorn chạy hàm này khi khởi động app
init_db()

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


@app.route('/admin/product/<int:product_id>', methods=['GET'])
def admin_get_product(product_id):
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'quantity': product.quantity,
            'image_url': product.image_url
        })
    except Exception as e:
        logger.error(f"Error getting product: {str(e)}")
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'}), 500


@app.route('/admin/add-product', methods=['POST'])
def admin_add_product():
    is_admin = session.get('is_admin', False)
    if not is_admin:
        flash('Không có quyền truy cập', 'error')
        return redirect(url_for('login'))
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price_str = request.form.get('price', '').strip()
    quantity_str = request.form.get('quantity', '').strip()
    image_url = request.form.get('image_url', '').strip()
    
    if not name or not price_str or not quantity_str:
        flash('Vui lòng điền đầy đủ Tên, Giá và Số lượng', 'error')
        return redirect(url_for('admin'))
    
    try:
        price = float(price_str)
        quantity = int(quantity_str)
        
        if price < 0 or quantity < 0:
            flash('Giá và số lượng không được âm', 'error')
            return redirect(url_for('admin'))
            
        product = Product(
            name=name, 
            description=description, 
            price=price, 
            quantity=quantity, 
            image_url=image_url if image_url else '/static/default.jpg'
        )
        db.session.add(product)
        db.session.commit()
        logger.info(f"Admin added product: {product.name}")
        
        flash('Thêm sản phẩm thành công!', 'success')
        return redirect(url_for('admin'))
        
    except ValueError:
        flash('Giá và số lượng phải là số hợp lệ', 'error')
        return redirect(url_for('admin'))
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        return redirect(url_for('admin'))


@app.route('/admin/update-product/<int:product_id>', methods=['POST'])
def admin_update_product(product_id):
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    try:
        product = Product.query.get_or_404(product_id)
        name = request.form.get('name', '').strip()
        price_str = request.form.get('price', '').strip()
        quantity_str = request.form.get('quantity', '').strip()
        
        if not name or not price_str or not quantity_str:
            return jsonify({'success': False, 'message': 'Thông tin không hợp lệ'}), 400
        
        product.name = name
        product.description = request.form.get('description', '').strip()
        product.price = float(price_str)
        product.quantity = int(quantity_str)
        product.image_url = request.form.get('image_url', '').strip() or product.image_url
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cập nhật thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    try:
        product = Product.query.get_or_404(product_id)
        # Chặn xóa nếu có đơn hàng
        if OrderItem.query.filter_by(product_id=product_id).first():
             return jsonify({'success': False, 'message': 'Sản phẩm đã có đơn hàng, không thể xóa'}), 400
             
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Xóa thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/adjust-inventory', methods=['POST'])
def admin_adjust_inventory():
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    try:
        product_id = request.form.get('product_id')
        adj_type = request.form.get('type')
        qty = int(request.form.get('quantity', 0))
        
        product = Product.query.get_or_404(product_id)
        if adj_type == 'in':
            product.quantity += qty
        else:
            if product.quantity < qty:
                return jsonify({'success': False, 'message': 'Tồn kho không đủ'}), 400
            product.quantity -= qty
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Điều chỉnh kho thành công'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/update-order-status/<int:order_id>', methods=['POST'])
def admin_update_order_status(order_id):
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    try:
        order = Order.query.get_or_404(order_id)
        order.status = request.form.get('status')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cập nhật trạng thái thành công'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/order/<int:order_id>', methods=['GET'])
def admin_view_order(order_id):
    is_admin = session.get('is_admin', False)
    if not is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    try:
        order = Order.query.get_or_404(order_id)
        items = [{'product_name': i.product.name, 'quantity': i.quantity, 'price': i.price} for i in order.items]
        return jsonify({'success': True, 'total': "{:,.0f}".format(order.total_price), 'items': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

@app.before_request
def before_request():
    pass # Bỏ bớt log thừa để tăng tốc độ

if __name__ == '__main__':
    # Vẫn giữ ở đây để khi bạn chạy python app.py ở local nó vẫn chạy
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)