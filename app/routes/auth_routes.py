from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import get_db_connection
from app.utils.logging import log_action
from app.forms.login_form import LoginForm
from app.forms.signup_form import SignupForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM User WHERE username = ? AND is_deleted = 0',
                           (form.username.data,)).fetchone()
        if user and check_password_hash(user['password_hash'], form.password.data):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = False
            flash('Login successful!', 'success')
            log_action('User', user['id'], 'LOGIN', f'User {form.username.data} logged in')
            conn.close()
            return redirect(url_for('main.home'))
        else:
            admin = conn.execute('SELECT * FROM Admin WHERE username = ? AND is_deleted = 0',
                               (form.username.data,)).fetchone()
            if admin and check_password_hash(admin['password_hash'], form.password.data):
                session['user_id'] = admin['id']
                session['username'] = admin['username']
                session['is_admin'] = True
                flash('Admin login successful!', 'success')
                log_action('Admin', admin['id'], 'LOGIN', f'Admin {form.username.data} logged in')
                conn.close()
                return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials.', 'error')
        log_action('Auth', 0, 'LOGIN_FAILED', f'Failed login attempt for username: {form.username.data}', error_code='AUTH_001')
        conn.close()
    return render_template('login.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM User WHERE username = ? OR email = ?',
                                   (form.username.data, form.email.data)).fetchone()
        if existing_user:
            flash('Username or email already exists.', 'error')
            log_action('User', 0, 'SIGNUP_FAILED', f'Failed signup: Username or email exists for {form.username.data}', error_code='AUTH_002')
            conn.close()
            return render_template('signup.html', form=form)
        password_hash = generate_password_hash(form.password.data)
        user_id = conn.execute(
            'INSERT INTO User (username, email, password_hash, created_by, updated_by) VALUES (?, ?, ?, ?, ?)',
            (form.username.data, form.email.data, password_hash, 'System', 'System')
        ).lastrowid
        conn.commit()
        flash('Signup successful! Please log in.', 'success')
        log_action('User', user_id, 'SIGNUP', f'User {form.username.data} signed up')
        conn.close()
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id', 0)
    username = session.get('username', 'Unknown')
    session.clear()
    flash('Logged out successfully.', 'success')
    log_action('User', user_id, 'LOGOUT', f'User {username} logged out')
    return redirect(url_for('main.home'))