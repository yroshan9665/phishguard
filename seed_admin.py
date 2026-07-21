"""
Creates the first admin user.
Usage: python seed_admin.py
"""
from app import create_app, db, bcrypt
from app.models import User

app = create_app()

with app.app_context():
    email    = input("Admin email: ").strip().lower()
    username = input("Admin username: ").strip()
    password = input("Admin password (min 8 chars): ").strip()

    if User.query.filter_by(email=email).first():
        print("User with this email already exists.")
    else:
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.add(User(username=username, email=email,
                            password=hashed, is_admin=True))
        db.session.commit()
        print(f"Admin user '{username}' created successfully.")
