import os
import re
from flask import render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Laptop
from flask import session

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def register_routes(app):
    @app.route('/')
    def index():
        laptops = Laptop.query.filter(Laptop.promotion.isnot(None)).all()
        per_page = 10  # Set your desired pagination size
        total = len(laptops)  # Or use laptops.count() if it's a query object
        page = request.args.get('page', 1, type=int)
        return render_template('index.html', laptops=laptops, total=total, per_page=per_page, page=page)

    @app.route('/product/<int:laptop_id>')
    def product(laptop_id):
        laptop = Laptop.query.get_or_404(laptop_id)
        return render_template('product.html', laptop=laptop)

    @app.route('/add_product', methods=['GET', 'POST'])
    @login_required
    def add_product():
        if current_user.role != 'admin':
            flash('Admins only!')
            return redirect(url_for('index'))
        if request.method == 'POST':
            brand = request.form['brand']
            model = request.form['model']
            specs = request.form['specs']
            price = float(request.form['price'])
            # Handle discount safely
            discount_str = request.form.get('discount', '0')
            discount = float(discount_str) if discount_str else 0.0
            promotion = request.form.get('promotion')


            stock = int(request.form.get('stock', 0))
            description = request.form.get('description')
            image_file = request.files.get('image')
            image_filename = None
            if image_file and image_file.filename:
                img_folder = os.path.join('static', 'images')
                os.makedirs(img_folder, exist_ok=True)
                image_filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(img_folder, image_filename))
            laptop = Laptop(
                brand=brand, model=model, specs=specs, price=price,
                discount=discount, promotion=promotion, stock=stock,
                description=description, image=image_filename
            )
            db.session.add(laptop)
            db.session.commit()
            flash('Product added!')
            return redirect(url_for('index'))
        return render_template('add_edit.html', laptop=None, action='Add', readonly=False)

    @app.route('/edit_product/<int:laptop_id>', methods=['GET', 'POST'])
    @login_required
    def edit_product(laptop_id):
        if current_user.role != 'admin':
            flash('Admins only!')
            return redirect(url_for('index'))
        laptop = Laptop.query.get_or_404(laptop_id)
        if request.method == 'POST':
            laptop.brand = request.form['brand']
            laptop.model = request.form['model']
            laptop.specs = request.form['specs']
            
            # Handle price and discount safely
            price_str = request.form.get('price', '0')
            laptop.price = float(price_str) if price_str else 0.0
            
            discount_str = request.form.get('discount', '0')
            laptop.discount = float(discount_str) if discount_str else 0.0
            
            # Handle stock safely
            stock_str = request.form.get('stock', '0')
            laptop.stock = int(stock_str) if stock_str else 0
            
            laptop.promotion = request.form.get('promotion')
            laptop.description = request.form.get('description')
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                img_folder = os.path.join('static', 'images')
                os.makedirs(img_folder, exist_ok=True)
                image_filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(img_folder, image_filename))
                laptop.image = image_filename
            db.session.commit()
            flash('Product updated!')
            return redirect(url_for('product', laptop_id=laptop.id))
        return render_template('add_edit.html', laptop=laptop, action='Update', readonly=False)

    @app.route('/delete/<int:laptop_id>', methods=['GET', 'POST'])
    @login_required
    def delete_product(laptop_id):
        if current_user.role != 'admin':
            abort(403)
        laptop = Laptop.query.get_or_404(laptop_id)
        if request.method == 'POST':
            db.session.delete(laptop)
            db.session.commit()
            flash('Laptop deleted successfully!', 'success')
            return redirect(url_for('index'))
        # Pass readonly=True to make fields non-editable in the template
        return render_template('add_edit.html', laptop=laptop, action='Delete', readonly=True)

    @app.route('/cart', methods=['GET', 'POST'])
    @login_required
    def cart():
        # Example: cart stored in session as a list of dicts
        cart_items = session.get('cart', [])
        # Calculate subtotal for each item and total
        for item in cart_items:
            price = item.get('price', 0)
            discount = item.get('discount', 0)
            quantity = item.get('quantity', 1)
            item['subtotal'] = price * quantity * (1 - discount / 100)
        total = sum(item['subtotal'] for item in cart_items) if cart_items else 0
        return render_template('cart.html', cart_items=cart_items, total=total)
    
    @app.route('/checkout', methods=['GET', 'POST'])
    @login_required
    def checkout():
        cart_items = session.get('cart', [])
        for item in cart_items:
            price = item.get('price', 0)
            discount = item.get('discount', 0)
            quantity = item.get('quantity', 1)
            item['subtotal'] = (price - discount) * quantity
        total = sum(item['subtotal'] for item in cart_items) if cart_items else 0
        if request.method == 'POST':
            # Handle order confirmation logic here
            flash('Order confirmed!')
            session['cart'] = []  # Clear cart after checkout
            return redirect(url_for('orders'))
        return render_template('checkout.html', cart_items=cart_items, total=total)

    @app.route('/orders')
    @login_required
    def orders():
        # Implement order history logic here
        return render_template('orders.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username_or_email = request.form.get('username')
            password = request.form.get('password')
    
            # Try to find user by username or email
            user = User.query.filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()
    
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                error = 'Invalid username/email or password.'
    
        return render_template('login.html', error=error)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form.get('role', 'user')
            if not is_valid_email(email):
                flash('Invalid email format.')
                return render_template('register.html')
            if User.query.filter_by(email=email).first():
                flash('Email already registered.')
                return render_template('register.html')
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/add_to_cart/<int:laptop_id>', methods=['POST'])
    @login_required
    def add_to_cart(laptop_id):
        # Get the cart from session, or create a new one
        cart = session.get('cart', [])
        # Check if laptop is already in cart (optional: support quantity)
        for item in cart:
            if item['id'] == laptop_id:
                item['quantity'] += 1
                break
        else:
            # Get laptop details from DB
            laptop = Laptop.query.get_or_404(laptop_id)
            cart.append({
                'id': laptop.id,
                'brand': laptop.brand,
                'model': laptop.model,
                'specs': laptop.specs,
                'price': laptop.price,
                'discount': laptop.discount,
                'quantity': 1,
                'image': laptop.image
            })
        session['cart'] = cart
        flash('Laptop added to cart!')
        return redirect(url_for('cart'))

    @app.route('/remove_from_cart/<int:laptop_id>', methods=['POST'])
    def remove_from_cart(laptop_id):
        cart = session.get('cart', [])
        cart = [item for item in cart if item['id'] != laptop_id]
        session['cart'] = cart
        flash('Item removed from cart!')
        return redirect(url_for('cart'))