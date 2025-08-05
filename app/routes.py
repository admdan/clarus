from flask import flash, Blueprint, render_template, request, redirect, url_for, make_response, current_app, abort
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from .models import get_user_by_username, verify_user, verify_reset_token, generate_reset_token, get_user_by_email, insert_user
from .db import get_db_connection
from datetime import datetime
from werkzeug.security import generate_password_hash
import smtplib
from email.mime.text import MIMEText

bp = Blueprint('routes', __name__)

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or getattr(current_user, 'role', None) not in roles:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


@bp.route('/', methods=['GET', 'POST'])
def login_register():
    # Force server-side redirection every time
    if current_user.is_authenticated:
        return redirect(url_for('routes.portal'))
    return render_template('index.html') # Animated login/register page

    # Disable caching explicitly at this route too
    #response = make_response(render_template('index.html'))
    #response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    #response.headers['Pragma'] = 'no-cache'
    #response.headers['Expires'] = '0'
    #return response

@bp.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    if not username or not email or not password:
        flash("All fields are required.", "register_error")
        return redirect(url_for('routes.login_register'))

    # Check if user exists
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    existing_user = cursor.fetchone()

    if existing_user:
        flash("User already exists. Try a different username or email.", "register_error")
        cursor.close()
        conn.close()
        return redirect(url_for('routes.login_register'))

    # Insert new user
    from .models import insert_user
    insert_user(username, email, password, )

    flash("Registration successful. Please login!", "register_success")
    return redirect(url_for('routes.login_register'))

@bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    remember = request.form.get('remember', False) == 'on' #true if checked, false otherwise

    if verify_user(username,password):
        user = get_user_by_username(username)
        login_user(user, remember=remember)

        if remember:
            flash("Login successful. Your session will be remembered for 7 days.", "login_success")
        else:
            flash("Login successful. You will be logged out when the browser is closed.","login_success")

        return redirect(url_for('routes.portal'))
    else:
        flash("Invalid username or password.", "login_error")
        return redirect(url_for('routes.login_register'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "logout")
    return redirect(url_for('routes.login_register'))

@bp.route('/forgot-password', methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip()

        # Lookup user by email
        user = get_user_by_email(email)
        if user:
            token = generate_reset_token(email, current_app.config['SECRET_KEY'], current_app.config['SALT'])
            reset_link = url_for('routes.reset_password', token=token, _external=True)

            #Email content
            subject = "Clarus - Password Reset Request"
            body = f"""
Hello {user['username']},

We received a request to reset your Clarus account password.

This link is valid only for 5 minutes. Click the link below to reset your password:
{reset_link}

If you did not request this, you can safely ignore this email.

- Clarus Support
"""
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = email

            # Send email via SMTP
            try:
                with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
                    smtp.send_message(msg)
            except Exception as e:
                print(f"Error sending email: {e}")
                flash("Error sending reset email. Please try again later.", "error")

        # Always flash the same message for security
        flash("If your email exists in our system, a reset link has been sent.", "info")

        return redirect(url_for('routes.login_register'))
    return render_template('forgot_password.html')

@bp.route('/reset-password/<token>', methods=['GET','POST'])
def reset_password(token):
    email = verify_reset_token(token, current_app.config['SECRET_KEY'], current_app.config['SALT'], expiration=300)

    if not email:
        flash("The reset link is invalid or has expired.", "error")
        return redirect(url_for('routes.forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords don't match. Please try again.", "error")
            return redirect(request.url)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''UPDATE users 
                          SET password_hash = %s 
                          WHERE email = %s''',
                       (hashed_password,email))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Password updated successfully. Please login to continue.", "success")
        return redirect(url_for('routes.login_register'))
    return render_template('reset_password.html', token=token)

@bp.route('/portal')
@login_required
def portal():
    modules = []
    role = getattr(current_user, 'role', 'basic')

    if role in ['admin']:
        modules.append('manage_role')
    if role in ['admin', 'support']:
        modules.append('troubleshooting')
    if role in ['admin', 'hr', 'support']:
        modules.append('inventory')
    if role in ['admin', 'hr', 'support']:
        modules.append('eip')

    modules.append('profile')

    welcome_message = f"Welcome back, {current_user.username}!"

    # Fetch notifications for this user
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT n.*, u.username AS sender_name
        FROM notifications n
        JOIN users u ON u.id = n.sender_id
        WHERE 
            (n.recipient_id IS NULL AND n.target_role IS NULL) OR
            (n.recipient_id = %s) OR
            (n.target_role = %s)
        ORDER BY n.created_at DESC
        LIMIT 10
    """, (current_user.id, role))

    notifications = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('portal.html',
                           modules=modules,
                           welcome_message=welcome_message,
                           notifications=notifications)


@bp.route('/manage-role')
@login_required
@roles_required('admin')
def manage_role():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('manage_role.html', users=users)

@bp.route('/aims')
@login_required
@roles_required('admin', 'hr', 'support')
def aims():
    return redirect(url_for('asset.inventory_dashboard'))

@bp.route('/post-notification', methods=['POST'])
@login_required
@roles_required('admin', 'hr', 'support')
def post_notification():
    message = request.form.get('message', '').strip()
    target_role = request.form.get('target_role', '').strip() or None
    recipient_username = request.form.get('recipient_username', '').strip() or None

    if not message:
        flash("Message cannot be empty.", "danger")
        return redirect(url_for('routes.portal'))

    recipient_id = None

    # If a specific user is targeted, look them up
    if recipient_username:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username = %s", (recipient_username,))
        user = cursor.fetchone()
        if not user:
            flash(f"User '{recipient_username}' not found.", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('routes.portal'))
        recipient_id = user['id']
        cursor.close()
        conn.close()

    # Insert notification into DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notifications (sender_id, recipient_id, target_role, message)
        VALUES (%s, %s, %s, %s)
    """, (current_user.id, recipient_id, target_role, message))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Notification posted successfully.", "success")
    return redirect(url_for('routes.portal'))
