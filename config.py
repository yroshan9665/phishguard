import os
from dotenv import load_dotenv

load_dotenv()

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY       = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    _db_url          = os.environ.get('DATABASE_URL', '')
    # Render gives postgres:// but SQLAlchemy needs postgresql://
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url if _db_url else f'sqlite:///{os.path.join(BASEDIR, "instance", "phishing.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REPORTS_DIR      = os.path.join(BASEDIR, 'reports')
    MODEL_PATH       = os.path.join(BASEDIR, 'app', 'ml', 'model.joblib')
    WTF_CSRF_ENABLED = True
