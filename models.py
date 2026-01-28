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
    conn.close()

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'user' or 'admin'

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