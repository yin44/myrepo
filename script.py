from main import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Define your desired admin username and password
    admin_username = 'admin'
    admin_email = 'admin@example.com' # Use a valid email format
    admin_password = 'adminpassword' # Choose a strong password for actual use!

    # Check if an admin user with this email already exists
    existing_admin = User.query.filter_by(email=admin_email).first()
    if existing_admin:
        print(f"Admin user with email '{admin_email}' already exists. Updating password and role if necessary.")
        existing_admin.password = generate_password_hash(admin_password)
        existing_admin.role = 'admin'
        db.session.commit()
        print(f"Updated password and ensured '{admin_email}' is an admin.")
    else:
        # Create a new admin user
        hashed_password = generate_password_hash(admin_password)
        new_admin = User(username=admin_username, email=admin_email, password=hashed_password, role='admin')
        db.session.add(new_admin)
        db.session.commit()
        print(f"New admin user '{admin_username}' created with email '{admin_email}' and password '{admin_password}'.")

    # Verify the admin user exists
    admin_user = User.query.filter_by(email=admin_email).first()
    if admin_user and admin_user.role == 'admin':
        print(f"Confirmation: User '{admin_user.username}' with email '{admin_user.email}' is an admin.")
    else:
        print("Failed to create/verify admin user.")