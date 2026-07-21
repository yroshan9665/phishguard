import os
from dotenv import load_dotenv

load_dotenv()

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY       = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///phishing.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REPORTS_DIR      = os.path.join(BASEDIR, 'reports')
    MODEL_PATH       = os.path.join(BASEDIR, 'app', 'ml', 'model.joblib')
    WTF_CSRF_ENABLED = True
