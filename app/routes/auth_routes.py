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
        conn = None
        try:
            conn = get_db_connection()
            user = conn.execute(
                'SELECT * FROM User WHERE email = ? AND is_deleted = 0',
                (form.email.data,)
            ).fetchone()

            if user and check_password_hash(user['password_hash'], form.password.data):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                session['is_admin'] = False
                flash('Login successful!', 'success')
                log_action('User', user['id'], 'LOGIN', f'User {form.email.data} logged in')
                return redirect(url_for('main.home'))

            admin = conn.execute(
                'SELECT * FROM Admin WHERE email = ? AND is_deleted = 0',
                (form.email.data,)
            ).fetchone()

            if admin and check_password_hash(admin['password_hash'], form.password.data):
                session['user_id'] = admin['id']
                session['username'] = admin['username']
                session['email'] = admin['email']
                session['is_admin'] = True
                flash('Admin login successful!', 'success')
                log_action('Admin', admin['id'], 'LOGIN', f'Admin {form.email.data} logged in')
                return redirect(url_for('admin.dashboard'))

            flash('Invalid credentials.', 'error')
            log_action('Auth', 0, 'LOGIN_FAILED', f'Failed login attempt for email: {form.email.data}', error_code='AUTH_001')

        except Exception as e:
            flash('An error occurred during login. Please try again later.', 'error')
            log_action('Auth', 0, 'LOGIN_EXCEPTION', f'Login error for {form.email.data}: {str(e)}', error_code='AUTH_EX_001')

        finally:
            if conn:
                conn.close()

    return render_template('login.html', form=form)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        conn = None
        try:
            conn = get_db_connection()
            existing_user = conn.execute(
                'SELECT * FROM User WHERE email = ?',
                (form.email.data,)
            ).fetchone()

            if existing_user:
                flash('Email already exists.', 'error')
                log_action('User', 0, 'SIGNUP_FAILED', f'Failed signup: email exists for {form.email.data}', error_code='AUTH_002')
                return render_template('signup.html', form=form)

            password_hash = generate_password_hash(form.password.data)

            user_id = conn.execute(
                'INSERT INTO User (username, email, password_hash, created_by, updated_by) VALUES (?, ?, ?, ?, ?)',
                (form.username.data, form.email.data, password_hash, form.email.data, '')
            ).lastrowid

            conn.commit()
            flash('Signup successful! Please log in.', 'success')
            log_action('User', user_id, 'SIGNUP', f'User {form.email.data} signed up')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash('An error occurred during signup. Please try again later.', 'error')
            log_action('User', 0, 'SIGNUP_EXCEPTION', f'Signup error for {form.email.data}: {str(e)}', error_code='AUTH_EX_002')

        finally:
            if conn:
                conn.close()

    return render_template('signup.html', form=form)


@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id', 0)
    email = session.get('email', 'Unknown')
    session.clear()
    flash('Logged out successfully.', 'success')
    log_action('User', user_id, 'LOGOUT', f'User {email} logged out')
    return redirect(url_for('main.home'))
