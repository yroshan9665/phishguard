from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    is_admin   = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scans = db.relationship('ScanResult', backref='user', lazy=True,
                            foreign_keys='ScanResult.user_id')


class ScanResult(db.Model):
    __tablename__ = 'scan_results'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    url         = db.Column(db.Text, nullable=False)
    prediction  = db.Column(db.String(20), nullable=False)
    confidence  = db.Column(db.Float, nullable=False)
    risk_score  = db.Column(db.Integer, nullable=False)
    features    = db.Column(db.JSON, default=dict)
    scanned_at  = db.Column(db.DateTime, default=datetime.utcnow)


class LoginLog(db.Model):
    __tablename__ = 'login_logs'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    status     = db.Column(db.String(10), default='success')  # success / failed
    logged_at  = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='login_logs', foreign_keys=[user_id])
