"""
Creates the first admin user from environment variables.
Set ADMIN_EMAIL, ADMIN_USERNAME, ADMIN_PASSWORD before running.
Safe to run multiple times — skips if admin already exists.
"""
import os
from app import create_app, db, bcrypt
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()

    email    = os.environ.get('ADMIN_EMAIL', '').strip().lower()
    username = os.environ.get('ADMIN_USERNAME', '').strip()
    password = os.environ.get('ADMIN_PASSWORD', '').strip()

    if not all([email, username, password]):
        print("Skipping admin seed: ADMIN_EMAIL, ADMIN_USERNAME, ADMIN_PASSWORD not set.")
    elif User.query.filter_by(email=email).first():
        print(f"Admin '{email}' already exists. Skipping.")
    else:
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.add(User(username=username, email=email,
                            password=hashed, is_admin=True))
        db.session.commit()
        print(f"Admin user '{username}' created successfully.")
