import sqlite3

DB_NAME = 'laptops.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS laptops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            specs TEXT,
            price REAL NOT NULL,
            discount REAL DEFAULT 0,
            promotion TEXT,
            image TEXT,
            stock INTEGER DEFAULT 0,
            description TEXT
        )
    ''')
    conn.commit()
    
    # Create fixed admin account if it doesn't exist
    from werkzeug.security import generate_password_hash
    cursor.execute('SELECT id FROM user WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        hashed_password = generate_password_hash('1234')
        cursor.execute('INSERT INTO user (username, email, password, role) VALUES (?, ?, ?, ?)', 
                      ('admin', 'admin@gmail.com', hashed_password, 'admin'))
        conn.commit()
    
    conn.close()

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'user' or 'admin'
    orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Laptop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    specs = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    promotion = db.Column(db.String(120))
    image = db.Column(db.String(120))
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Laptop {self.brand} {self.model}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending') # e.g., Pending, Shipped, Delivered, Cancelled
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    shipping_address = db.Column(db.Text, nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    laptop_id = db.Column(db.Integer, db.ForeignKey('laptop.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_purchase = db.Column(db.Float, nullable=False) # Price of one item at the time of purchase
    laptop = db.relationship('Laptop')

    def __repr__(self):
        return f'<OrderItem {self.id}>'