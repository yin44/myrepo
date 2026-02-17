import re
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, User
import routes
from dotenv import load_dotenv
from flask_mail import Mail

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key')
# Use an absolute path for the database URI to ensure consistency
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'laptops.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

db.init_app(app)
mail = Mail(app)  # Initialize Flask-Mail

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#to load user object from database given user_id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 

routes.register_routes(app, mail)

def get_db_file_path(app):
    """Extracts the absolute path to the SQLite database file from SQLALCHEMY_DATABASE_URI."""
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    match = re.match(r'sqlite:///(.*)', uri)
    if match:
        db_file = match.group(1)
        if not os.path.isabs(db_file):
            # If it's a relative path (like 'laptops.db'), assume it's relative to the CWD
            # where the Flask app is typically run from.
            return os.path.join(os.getcwd(), db_file)
        return db_file
    return None # Should not happen for sqlite:/// URIs

def add_customer_email_column():
    """Adds the customer_email column to the order table if it doesn't exist."""
    import sqlite3
    
    db_path = get_db_file_path(app) # Use the consistent path
    if not db_path:
        print("Could not determine database file path from SQLALCHEMY_DATABASE_URI.")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the 'order' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order';")
        if cursor.fetchone():
            # Check if 'customer_email' column exists in 'order' table
            cursor.execute("PRAGMA table_info(\"order\")")
            columns = [col[1] for col in cursor.fetchall()]

            if 'customer_email' not in columns:
                cursor.execute("ALTER TABLE \"order\" ADD COLUMN customer_email VARCHAR(120)")
                conn.commit()
                print(f"Successfully added 'customer_email' column to the 'order' table in {db_path}.")
            else:
                print(f"'customer_email' column already exists in the 'order' table in {db_path}.")
        else:
            print(f"'order' table does not exist yet in {db_path}. It will be created by db.create_all().")

    except sqlite3.Error as e:
        print(f"Database error during migration check for {db_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during migration check for {db_path}: {e}")
    finally:
        if conn:
            conn.close()

def add_is_deleted_column():
    """Adds the is_deleted column to the order table if it doesn't exist."""
    import sqlite3
    
    db_path = get_db_file_path(app) # Use the consistent path
    if not db_path:
        print("Could not determine database file path from SQLALCHEMY_DATABASE_URI.")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the 'order' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order';")
        if cursor.fetchone():
            # Check if 'is_deleted' column exists in 'order' table
            cursor.execute("PRAGMA table_info(\"order\")")
            columns = [col[1] for col in cursor.fetchall()]

            if 'is_deleted' not in columns:
                cursor.execute("ALTER TABLE \"order\" ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE")
                conn.commit()
                print(f"Successfully added 'is_deleted' column to the 'order' table in {db_path}.")
            else:
                print(f"'is_deleted' column already exists in the 'order' table in {db_path}.")
        else:
            print(f"'order' table does not exist yet in {db_path}. It will be created by db.create_all().")

    except sqlite3.Error as e:
        print(f"Database error during migration check for {db_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during migration check for {db_path}: {e}")
    finally:
        if conn:
            conn.close()

with app.app_context():
    add_customer_email_column()
    add_is_deleted_column()
    db.create_all()

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=True)