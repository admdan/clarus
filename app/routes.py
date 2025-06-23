from flask import Blueprint, render_template, request, redirect, url_for, make_response
from flask_login import login_user, logout_user, current_user, login_required
from .models import get_user_by_username, verify_user
from .db import get_db_connection
from datetime import datetime
from flask import flash

bp = Blueprint('routes', __name__)

@bp.route('/', methods=['GET', 'POST'])
def login_register():
    # Force server-side redirect every time
    if current_user.is_authenticated:
        return redirect(url_for('troubleshooting.troubleshooting_dashboard'))
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
        flash("All fields are required.", "error")
        return redirect(url_for('routes.login_register'))

    # Check if user exists
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    existing_user = cursor.fetchone()

    if existing_user:
        flash("User already exists. Try a different username or email.", "error")
        cursor.close()
        conn.close()
        return redirect(url_for('routes.login_register'))

    # Insert new user
    from .models import insert_user
    insert_user(username, email, password)

    flash("Registration successful. Please login!", "success")
    return redirect(url_for('routes.login_register'))

@bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if verify_user(username,password):
        user = get_user_by_username(username)
        login_user(user)
        flash("Login successful", "success")
        return redirect(url_for('troubleshooting.troubleshooting_dashboard'))
    else:
        flash("Invalid username or password.", "error")
        return redirect(url_for('routes.login_register'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "success")
    return redirect(url_for('routes.login_register'))

@bp.route('/add', methods=('GET', 'POST'))
def add_ticket():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        user_name = request.form['user_name']
        issue_description = request.form['issue_description']
        device_type = request.form['device_type']
        date_reported = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        prefix_map = {
            'Desktop': 'PC',
            'Laptop': 'LP',
            'Mobile': 'PH',
            'Printer': 'PR',
            'Router': 'RT',
            'Switch': 'SW',
            'Tablet': 'TB',
            'Other': 'OT'
        }
        prefix = prefix_map.get(device_type, 'OT')

        # Generate device_code like PC0002
        cursor.execute('''SELECT device_code 
                          FROM devices 
                          WHERE device_code 
                                    LIKE %s 
                          ORDER BY device_code 
                              DESC LIMIT 1''',
                       (prefix + '%',))
        last = cursor.fetchone()

        if last and last['device_code'][len(prefix):].isdigit():
            last_number = int(last['device_code'][len(prefix):])
            new_number = last_number + 1
        else:
            new_number = 1

        device_code = f"{prefix}{new_number:04}"  # e.g., PC0001

        # Insert new device with just type and code
        cursor.execute('''
                       INSERT INTO devices (device_type, device_code)
                       VALUES (%s, %s)
                       ''', (device_type, device_code))

        device_id = cursor.lastrowid

        # Insert into tickets table
        cursor.execute('''
                       INSERT INTO tickets (user_name, device_id, issue_description, date_reported)
                       VALUES (%s, %s, %s, %s)
                       ''', (user_name, device_id, issue_description, date_reported))

        conn.commit()
        return redirect(url_for('routes.confirmation', code=device_code))
    conn.close()
    return render_template('add_ticket.html')

@bp.route('/delete/<int:id>', methods=('POST',))
def delete_ticket(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tickets WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    flash('Ticket deleted successfully!', 'success')
    return redirect(url_for('routes.index'))

@bp.route('/confirmation')
def confirmation():
    code = request.args.get('code')
    return render_template('confirmation.html', device_code=code)
