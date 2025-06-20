from flask import Blueprint, render_template, request, redirect, url_for
from .db import get_db_connection
from datetime import datetime
from flask import flash

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
                   SELECT t.id,
                          t.user_name,
                          d.device_code,
                          t.issue_description,
                          t.date_reported,
                          t.troubleshooting,
                          t.status
                   FROM tickets t
                            JOIN devices d ON t.device_id = d.device_id
                   ''')
    tickets = cursor.fetchall()

    conn.close()
    return render_template('index.html', tickets=tickets)

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
