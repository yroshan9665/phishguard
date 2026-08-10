import re
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, LoginLog

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

_reset_tokens = {}


def _clean_tokens():
    now = datetime.utcnow()
    for k in [k for k, v in _reset_tokens.items() if v['expires'] < now]:
        del _reset_tokens[k]


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not all([username, email, password, confirm]):
            flash('All fields are required.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        elif len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
        elif not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter.', 'danger')
        elif not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter.', 'danger')
        elif not re.search(r'[0-9]', password):
            flash('Password must contain at least one number.', 'danger')
        elif User.query.filter((User.email == email) | (User.username == username)).first():
            flash('Username or email already registered.', 'danger')
        else:
            hashed = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.add(User(username=username, email=email, password=hashed))
            db.session.commit()
            flash('Account created! Please sign in.', 'success')
            return redirect(url_for('auth.login'))
        return redirect(url_for('auth.register'))
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email, is_admin=False).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=bool(request.form.get('remember')))
            db.session.add(LoginLog(user_id=user.id, ip_address=request.remote_addr, status='success'))
            db.session.commit()
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard.index'))
        # check if it's an admin trying to use user login
        admin_user = User.query.filter_by(email=email, is_admin=True).first()
        if admin_user and bcrypt.check_password_hash(admin_user.password, password):
            flash('Admin accounts must use the Admin Login portal.', 'warning')
            return redirect(url_for('admin.admin_login'))
        if user or admin_user:
            u = user or admin_user
            db.session.add(LoginLog(user_id=u.id, ip_address=request.remote_addr, status='failed'))
            db.session.commit()
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    email    = current_user.email
    logout_user()
    return render_template('auth/logout.html', username=username, email=email)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = User.query.filter_by(email=email).first()
        if user:
            _clean_tokens()
            token = secrets.token_urlsafe(32)
            _reset_tokens[token] = {
                'user_id': user.id,
                'expires': datetime.utcnow() + timedelta(minutes=30)
            }
            session['dev_reset_url']   = url_for('auth.reset_password', token=token, _external=True)
            session['dev_reset_email'] = email
        flash('If that email is registered, a reset link has been generated.', 'info')
        return redirect(url_for('auth.forgot_password'))
    dev_url   = session.pop('dev_reset_url', None)
    dev_email = session.pop('dev_reset_email', None)
    return render_template('auth/forgot_password.html', dev_url=dev_url, dev_email=dev_email)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    _clean_tokens()
    token_data = _reset_tokens.get(token)
    if not token_data or token_data['expires'] < datetime.utcnow():
        flash('This reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        if not password or not confirm:
            flash('Both fields are required.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        elif len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
        elif not re.search(r'[A-Z]', password):
            flash('Include at least one uppercase letter.', 'danger')
        elif not re.search(r'[a-z]', password):
            flash('Include at least one lowercase letter.', 'danger')
        elif not re.search(r'[0-9]', password):
            flash('Include at least one number.', 'danger')
        else:
            user = User.query.get(token_data['user_id'])
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.commit()
            del _reset_tokens[token]
            flash('Password reset successfully! Please sign in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', token=token)
