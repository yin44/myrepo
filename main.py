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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///laptops.db'
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


with app.app_context():
    db.create_all()

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=True)