import os
from flask import redirect, url_for
from app import create_app, db, bcrypt
from dotenv import load_dotenv

load_dotenv()
app = create_app()

@app.route('/')
def home():
    return redirect(url_for('auth.login'))

# Auto-initialize database, ML model, and admin account on cloud startup
with app.app_context():
    db.create_all()

    # Train ML model if not already present
    model_path = app.config.get('MODEL_PATH', os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'ml', 'model.joblib'))
    if not os.path.exists(model_path):
        try:
            from app.ml.train_model import train
            train()
        except Exception as e:
            print(f"ML Model initialization notice: {e}")

    # Ensure default admin account exists
    from app.models import User
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@phishguard.ai')
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'Admin@1234')
        admin_uname = os.environ.get('ADMIN_USERNAME', 'admin')
        hashed = bcrypt.generate_password_hash(admin_pass).decode('utf-8')
        db.session.add(User(
            username=admin_uname,
            email=admin_email,
            password=hashed,
            is_admin=True
        ))
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
