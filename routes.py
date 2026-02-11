import os
import re
from flask import render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Laptop, Order, OrderItem
from flask import session

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def register_routes(app, mail):
    @app.route('/')
    def index():
        page = request.args.get('page', 1, type=int)
        per_page = 6
        search_query = request.args.get('search')
        if search_query:
            laptops_pagination = Laptop.query.filter(Laptop.brand.ilike(f'%{search_query}%')).paginate(page=page, per_page=per_page, error_out=False)
        else:
            # This logic creates the desired sorting order:
            # 1. Items with a promotion tag are prioritized first.
            # 2. Then, items with a discount are prioritized.
            # 3. Finally, regular items are shown.
            # Within each group, items are sorted by their creation ID.
            laptops_pagination = Laptop.query.order_by(
                (Laptop.promotion.isnot(None) & (Laptop.promotion != '')).desc(),
                (Laptop.discount > 0).desc(),
                Laptop.id.asc()
            ).paginate(page=page, per_page=per_page, error_out=False)
        laptops = laptops_pagination.items
        return render_template('index.html', laptops=laptops, pagination=laptops_pagination)

    @app.route('/product/<int:laptop_id>')
    def product(laptop_id):
        laptop = Laptop.query.get_or_404(laptop_id)
        return render_template('product.html', laptop=laptop)

<<<<<<< HEAD
=======
    def send_order_email(order, customer_email, status):
        """Send email notification for order status changes"""
        try:
            subject = f"Your Order #{order.id} - {status}"
            msg = Message(subject,
                          sender=("LaptopSales", os.environ.get('MAIL_USERNAME')),
                          recipients=[customer_email])
            
            # Get order items for email
            order_items = []
            for item in order.items:
                order_items.append({
                    'brand': item.laptop.brand,
                    'model': item.laptop.model,
                    'quantity': item.quantity,
                    'price': item.price_at_purchase,
                    'subtotal': item.price_at_purchase * item.quantity
                })
            
            msg.html = render_template('order_status_email.html', 
                                     order=order, 
                                     status=status,
                                     items=order_items,
                                     customer_name=order.customer.username)
            mail.send(msg)
            return True
        except Exception as e:
            app.logger.error(f"Failed to send email: {e}")
            return False

>>>>>>> e1ea81e (email sent for ever status , error messages)
    @app.route('/add_product', methods=['GET', 'POST'])
    @login_required
    def add_product():
        if current_user.role != 'admin':
            flash('Admins only!')
            return redirect(url_for('index'))
        if request.method == 'POST':
<<<<<<< HEAD
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
=======
            # Enhanced validation
            errors = []
            
            brand = request.form.get('brand', '').strip()
            model = request.form.get('model', '').strip()
            specs = request.form.get('specs', '').strip()
            
            if not brand:
                errors.append('Brand is required')
            if not model:
                errors.append('Model is required')
            if not specs:
                errors.append('Specs are required')
            
            # Price validation
            try:
                price_str = request.form.get('price', '0').strip()
                price = float(price_str) if price_str else 0.0
                if price <= 0:
                    errors.append('Price must be greater than 0')
            except (ValueError, TypeError):
                errors.append('Invalid price format')
                price = 0.0
            
            # Discount validation
            try:
                discount_str = request.form.get('discount', '0').strip()
                discount = float(discount_str) if discount_str else 0.0
                if discount < 0 or discount > 100:
                    errors.append('Discount must be between 0 and 100')
            except (ValueError, TypeError):
                errors.append('Invalid discount format')
                discount = 0.0
            
            # Stock validation
            try:
                stock_str = request.form.get('stock', '0').strip()
                stock = int(stock_str) if stock_str else 0
                if stock < 0:
                    errors.append('Stock cannot be negative')
            except (ValueError, TypeError):
                errors.append('Invalid stock format')
                stock = 0
            
            promotion = request.form.get('promotion', '').strip()
            description = request.form.get('description', '').strip()
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('add_edit.html', laptop=request.form, action='Add', readonly=False)
            
            # Handle image upload
>>>>>>> e1ea81e (email sent for ever status , error messages)
            image_file = request.files.get('image')
            image_filename = None
            if image_file and image_file.filename:
                img_folder = os.path.join('static', 'images')
                os.makedirs(img_folder, exist_ok=True)
                image_filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(img_folder, image_filename))
<<<<<<< HEAD
=======
            
>>>>>>> e1ea81e (email sent for ever status , error messages)
            laptop = Laptop(
                brand=brand, model=model, specs=specs, price=price,
                discount=discount, promotion=promotion, stock=stock,
                description=description, image=image_filename
            )
            db.session.add(laptop)
            db.session.commit()
<<<<<<< HEAD
            flash('Product added!')
=======
            flash('Product added successfully!', 'success')
>>>>>>> e1ea81e (email sent for ever status , error messages)
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
<<<<<<< HEAD
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
=======
            # Enhanced validation
            errors = []
            
            brand = request.form.get('brand', '').strip()
            model = request.form.get('model', '').strip()
            specs = request.form.get('specs', '').strip()
            
            if not brand:
                errors.append('Brand is required')
            if not model:
                errors.append('Model is required')
            if not specs:
                errors.append('Specs are required')
            
            # Price validation
            try:
                price_str = request.form.get('price', '0').strip()
                price = float(price_str) if price_str else 0.0
                if price <= 0:
                    errors.append('Price must be greater than 0')
            except (ValueError, TypeError):
                errors.append('Invalid price format')
                price = 0.0
            
            # Discount validation
            try:
                discount_str = request.form.get('discount', '0').strip()
                discount = float(discount_str) if discount_str else 0.0
                if discount < 0 or discount > 100:
                    errors.append('Discount must be between 0 and 100')
            except (ValueError, TypeError):
                errors.append('Invalid discount format')
                discount = 0.0
            
            # Stock validation
            try:
                stock_str = request.form.get('stock', '0').strip()
                stock = int(stock_str) if stock_str else 0
                if stock < 0:
                    errors.append('Stock cannot be negative')
            except (ValueError, TypeError):
                errors.append('Invalid stock format')
                stock = 0
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('add_edit.html', laptop=laptop, action='Update', readonly=False)
            
            # Update laptop data
            laptop.brand = brand
            laptop.model = model
            laptop.specs = specs
            laptop.price = price
            laptop.discount = discount
            laptop.stock = stock
            laptop.promotion = request.form.get('promotion', '').strip()
            laptop.description = request.form.get('description', '').strip()
            
            # Handle image upload
>>>>>>> e1ea81e (email sent for ever status , error messages)
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                img_folder = os.path.join('static', 'images')
                os.makedirs(img_folder, exist_ok=True)
                image_filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(img_folder, image_filename))
                laptop.image = image_filename
<<<<<<< HEAD
            db.session.commit()
            flash('Product updated!')
=======
            
            db.session.commit()
            flash('Product updated successfully!', 'success')
>>>>>>> e1ea81e (email sent for ever status , error messages)
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
        if not cart_items:
            flash('Your cart is empty.')
            return redirect(url_for('cart'))

        grand_total = 0
        for item in cart_items:
            price = item.get('price', 0)
            discount = item.get('discount', 0)
            quantity = item.get('quantity', 1)
            final_price = price * (1 - discount / 100)
            item['subtotal'] = final_price * quantity
            grand_total += item['subtotal']

        if request.method == 'POST':
            customer_name = request.form.get('name')
            shipping_address = request.form.get('address')
            customer_email = request.form.get('email')
            if not shipping_address:
                flash('Shipping address is required.', 'error')
                return render_template('checkout.html', cart_items=cart_items, total=grand_total)
            if not customer_email:
                flash('Email address is required.', 'error')
                return render_template('checkout.html', cart_items=cart_items, total=grand_total)

            # Create the Order
            new_order = Order(
                user_id=current_user.id,
                total_price=grand_total,
                shipping_address=shipping_address,
<<<<<<< HEAD
                status='Pending'
=======
                status='Pending',
                customer_email=customer_email  # Store the email from checkout
>>>>>>> e1ea81e (email sent for ever status , error messages)
            )
            db.session.add(new_order)
            db.session.commit() # Commit to get the new_order.id

            # Create OrderItems and update stock
            for item in cart_items:
                laptop = Laptop.query.get(item['id'])
                if laptop and laptop.stock >= item['quantity']:
                    price_at_purchase = laptop.price * (1 - (laptop.discount or 0) / 100)
                    
                    order_item = OrderItem(
                        order_id=new_order.id,
                        laptop_id=item['id'],
                        quantity=item['quantity'],
                        price_at_purchase=price_at_purchase
                    )
                    db.session.add(order_item)
                    
                    # Decrement stock
                    laptop.stock -= item['quantity']
                else:
                    # Not enough stock, this is a simplified handling.
                    flash(f"Sorry, {item['brand']} {item['model']} is out of stock.", 'error')
                    db.session.rollback() # Rollback the transaction
                    return redirect(url_for('cart'))

            db.session.commit()

            # Send confirmation email
            try:
                msg = Message("Your Order Confirmation",
                              sender=("LaptopSales", os.environ.get('MAIL_USERNAME')),
                              recipients=[customer_email])
                msg.html = render_template('order_confirmation_email.html', order=new_order, customer_name=customer_name, items=cart_items, total=grand_total)
                mail.send(msg)
                flash('Your order has been placed and a confirmation email has been sent!', 'success')
            except Exception as e:
                app.logger.error(f"Failed to send email: {e}")
                flash('Your order has been placed, but we failed to send a confirmation email. Please contact support.', 'warning')

            # Clear the cart
            session['cart'] = []
            return redirect(url_for('index'))

        return render_template('checkout.html', cart_items=cart_items, total=grand_total)



    @app.route('/admin/orders')
    @login_required
    def admin_orders():
        if current_user.role != 'admin':
            flash('Admins only!', 'error')
            return redirect(url_for('index'))
        
<<<<<<< HEAD
        all_orders = Order.query.order_by(Order.order_date.desc()).all()
=======
        # Exclude soft-deleted orders
        all_orders = Order.query.filter_by(is_deleted=False).order_by(Order.order_date.desc()).all()
>>>>>>> e1ea81e (email sent for ever status , error messages)
        return render_template('admin_orders.html', orders=all_orders)

    @app.route('/admin/order/<int:order_id>')
    @login_required
    def admin_order_details(order_id):
        if current_user.role != 'admin':
            flash('Admins only!', 'error')
            return redirect(url_for('index'))
        
        order = Order.query.get_or_404(order_id)
        return render_template('admin_order_details.html', order=order)

    @app.route('/admin/order/update_status/<int:order_id>', methods=['POST'])
    @login_required
    def update_order_status(order_id):
        if current_user.role != 'admin':
            flash('Admins only!', 'error')
            return redirect(url_for('index'))

        order = Order.query.get_or_404(order_id)
        new_status = request.form.get('status')

        if new_status in ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled']:
<<<<<<< HEAD
            order.status = new_status
            db.session.commit()
            flash(f'Order #{order.id} status updated to {new_status}.', 'success')
=======
            old_status = order.status
            order.status = new_status
            db.session.commit()
            
            # Send email notification for status changes
            if new_status in ['Confirmed', 'Shipped', 'Delivered', 'Cancelled']:
                customer_email = order.customer_email  # Use email from checkout, not login email
                if customer_email:
                    email_sent = send_order_email(order, customer_email, new_status)
                    if email_sent:
                        flash(f'Order #{order.id} status updated to {new_status} and email notification sent.', 'success')
                    else:
                        flash(f'Order #{order.id} status updated to {new_status} but email notification failed.', 'warning')
                else:
                    flash(f'Order #{order.id} status updated to {new_status}.', 'success')
            else:
                flash(f'Order #{order.id} status updated to {new_status}.', 'success')
>>>>>>> e1ea81e (email sent for ever status , error messages)
        else:
            flash('Invalid status update.', 'error')
        
        return redirect(url_for('admin_orders'))

    @app.route('/admin/order/delete/<int:order_id>', methods=['POST'])
    @login_required
    def delete_order(order_id):
        if current_user.role != 'admin':
            flash('Admins only!', 'error')
            return redirect(url_for('index'))

        order = Order.query.get_or_404(order_id)
        
<<<<<<< HEAD
        # Optional: Add checks here, e.g., only allow deletion for cancelled orders
        
        db.session.delete(order)
        db.session.commit()
        
        flash(f'Order #{order.id} has been deleted.', 'success')
=======
        # Soft delete - mark as deleted instead of removing from database
        order.is_deleted = True
        db.session.commit()
        
        flash(f'Order #{order.id} has been soft deleted.', 'success')
>>>>>>> e1ea81e (email sent for ever status , error messages)
        return redirect(url_for('admin_orders'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username_or_email = request.form.get('username')
            password = request.form.get('password')

            # Try to find user by username or email
            user = User.query.filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username/email or password.', 'error')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
<<<<<<< HEAD
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = 'user'  # Always create regular users, not admins
            if not is_valid_email(email):
                flash('Invalid email format.')
                return render_template('register.html')
            if User.query.filter_by(email=email).first():
                flash('Email already registered.')
=======
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            role = 'user'  # Always create regular users, not admins
            
            # Validate required fields
            if not username:
                flash('Username is required', 'error')
                return render_template('register.html')
            if not email:
                flash('Email is required', 'error')
                return render_template('register.html')
            if not password:
                flash('Password is required', 'error')
                return render_template('register.html')
                
            if not is_valid_email(email):
                flash('Invalid email format.', 'error')
                return render_template('register.html')
            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'error')
>>>>>>> e1ea81e (email sent for ever status , error messages)
                return render_template('register.html')
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
<<<<<<< HEAD
            flash('Registration successful. Please log in.')
=======
            flash('Registration successful. Please log in.', 'success')
>>>>>>> e1ea81e (email sent for ever status , error messages)
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/add_to_cart/<int:laptop_id>', methods=['POST'])
    @login_required
    def add_to_cart(laptop_id):
        laptop = Laptop.query.get_or_404(laptop_id)
        cart = session.get('cart', [])
        
        found_item = None
        for item in cart:
            if item['id'] == laptop_id:
                found_item = item
                break
        
        if found_item:
            # Check against stock before increasing quantity
            if laptop.stock > found_item['quantity']:
                found_item['quantity'] += 1
                flash('Laptop quantity updated in cart!')
            else:
                flash(f'Sorry, only {laptop.stock} of {laptop.brand} {laptop.model} available.', 'error')
        else:
            # Check against stock before adding a new item
            if laptop.stock > 0:
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
                flash('Laptop added to cart!')
            else:
                flash(f'Sorry, {laptop.brand} {laptop.model} is out of stock.', 'error')
        
        session['cart'] = cart
<<<<<<< HEAD
        # Flash a confirmation and return to the referrer (page where add was triggered)
        # if referrer is not available, fall back to index
        ref = request.referrer or url_for('index')
        return redirect(ref)
=======
        # Redirect to cart page after adding item
        return redirect(url_for('cart'))
>>>>>>> e1ea81e (email sent for ever status , error messages)

    @app.route('/remove_from_cart/<int:laptop_id>', methods=['POST'])
    def remove_from_cart(laptop_id):
        cart = session.get('cart', [])
        cart = [item for item in cart if item['id'] != laptop_id]
        session['cart'] = cart
        flash('Item removed from cart!')
        return redirect(url_for('cart'))