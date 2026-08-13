from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.database import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter your email and password.', 'warning')
            return render_template('pages/auth/login.html')

        user = User.query.filter_by(email=email).first()
        if user and user.is_active and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return _redirect_by_role(user)
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('pages/auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        account_type = request.form.get('account_type', 'TRAVELER')

        # Validation
        if not name or not email or not password:
            flash('All fields are required.', 'warning')
            return render_template('pages/auth/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'warning')
            return render_template('pages/auth/register.html')

        if account_type not in ('TRAVELER', 'PARTNER'):
            account_type = 'TRAVELER'

        if User.query.filter_by(email=email).first():
            flash('This email is already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        user = User(name=name, email=email, role=account_type)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Welcome to Yatrik, {name}!', 'success')
        return _redirect_by_role(user)

    return render_template('pages/auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


def _redirect_by_role(user):
    """Redirect user to the appropriate page based on their role."""
    if user.is_admin:
        return redirect('/admin-yatrik-secret')
    elif user.is_partner:
        return redirect(url_for('partner.dashboard'))
    else:
        return redirect(url_for('main.home'))
