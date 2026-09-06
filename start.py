"""
PhishGuard AI — Single startup script
--------------------------------------
Run this ONE file to start the entire app:

    python start.py

It will automatically:
  1. Check all required packages are installed
  2. Train the ML model if model.joblib is missing
  3. Create the database tables if they don't exist
  4. Create the admin user if one doesn't exist yet
  5. Start the Flask development server at http://localhost:5000

Admin credentials (edit below or set in .env):
  ADMIN_USERNAME = admin
  ADMIN_EMAIL    = admin@phishguard.ai
  ADMIN_PASSWORD = Admin@1234
"""

import os
import sys

# ── 1. Dependency check ──────────────────────────────────────────────────────
REQUIRED = [
    "flask", "flask_sqlalchemy", "flask_login", "flask_bcrypt",
    "flask_wtf", "sqlalchemy", "sklearn", "pandas", "numpy",
    "requests", "bs4", "whois", "reportlab", "joblib", "dotenv",
]

missing = []
for pkg in REQUIRED:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print("=" * 55)
    print("  Missing packages detected. Installing now...")
    print("=" * 55)
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    print("\nDone. Restarting...\n")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# ── 2. Load app ──────────────────────────────────────────────────────────────
from app import create_app, db, bcrypt
from dotenv import load_dotenv

load_dotenv()
app = create_app()

@app.route('/')
def home():
    from flask import redirect, url_for
    return redirect(url_for('auth.login'))

# ── 3. Train model if missing ────────────────────────────────────────────────
MODEL_PATH = os.path.join("app", "ml", "model.joblib")
if not os.path.exists(MODEL_PATH):
    print("=" * 55)
    print("  ML model not found — training now (one-time setup)...")
    print("=" * 55)
    from app.ml.train_model import train
    train()
    print("  Model trained and saved.\n")

# ── 4. Init DB + create admin ────────────────────────────────────────────────
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_EMAIL    = os.environ.get("ADMIN_EMAIL",    "admin@phishguard.ai")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@1234")

with app.app_context():
    db.create_all()

    from app.models import User
    if not User.query.filter_by(is_admin=True).first():
        hashed = bcrypt.generate_password_hash(ADMIN_PASSWORD).decode("utf-8")
        db.session.add(User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=hashed,
            is_admin=True,
        ))
        db.session.commit()
        print("=" * 55)
        print("  Admin account created:")
        print(f"    Email    : {ADMIN_EMAIL}")
        print(f"    Password : {ADMIN_PASSWORD}")
        print("  Change these credentials after first login!")
        print("=" * 55 + "\n")
    else:
        print("  Admin account already exists. Skipping.\n")

# ── 5. Start server ──────────────────────────────────────────────────────────
print("=" * 55)
print("  PhishGuard AI is running!")
print("  Open: http://localhost:5000")
print("  Press Ctrl+C to stop.")
print("=" * 55 + "\n")

app.run(debug=True, host="0.0.0.0", port=5000)
