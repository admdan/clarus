import psycopg2.extras
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.routes import roles_required
from .db import get_db_connection
from datetime import datetime

troubleshooting_bp = Blueprint('troubleshooting', __name__, url_prefix='/troubleshooting')

@troubleshooting_bp.route('/', methods=['GET'])
@login_required
@roles_required('admin', 'support')
def troubleshooting_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Always fetch 5 most recently updated tickets
    cursor.execute('''
                   SELECT id, issue_description, last_updated 
                   FROM tickets 
                   ORDER BY last_updated DESC 
                   LIMIT 5''')
    recently_updated = cursor.fetchall()

    # Filters
    query = request.args.get('query', '').strip()
    status_filter = request.args.get('status', 'All')

    sql = '''
          SELECT t.id, 
                 t.user_name, 
                 d.device_code, 
                 d.device_type,
                 t.issue_description, 
                 t.troubleshooting,
                 t.status, 
                 t.date_reported, 
                 t.due_date,
                 t.priority, 
                 t.category, 
                 t.assigned_to
          FROM tickets t
                   JOIN devices d ON t.device_id = d.device_id
          WHERE 1 = 1 
          '''

    params = []

    if query:
        sql += " AND (t.user_name ILIKE %s OR d.device_code ILIKE %s OR t.issue_description ILIKE %s)"
        q = f"%{query}%"
        params += [q, q, q]

    if status_filter != 'All':
        sql += " AND t.status = %s"
        params.append(status_filter)

    sql += " ORDER BY t.last_updated DESC"
    cursor.execute(sql, params)
    filtered_tickets = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'troubleshooting.html',
        tickets=filtered_tickets,
        recently_updated=recently_updated,
        query=query,
        selected_status=status_filter
    )

@troubleshooting_bp.route('/add', methods=('GET', 'POST'))
@login_required
@roles_required('admin', 'support')
def add_ticket():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
        cursor.execute('''
                       SELECT device_code
                       FROM devices
                       WHERE device_code ILIKE %s
                       ORDER BY device_code DESC
                       LIMIT 1
                       ''', (prefix + '%',))
        last = cursor.fetchone()

        if last and last['device_code'][len(prefix):].isdigit():
            last_number = int(last['device_code'][len(prefix):])
            new_number = last_number + 1
        else:
            new_number = 1

        device_code = f"{prefix}{new_number:04}"  # e.g., PC0001

        # Insert a new device with just type and code
        cursor.execute('''
                       INSERT INTO devices (device_type, device_code)
                       VALUES (%s, %s)
                       RETURNING device_id
                       ''', (device_type, device_code))
        device_id = cursor.fetchone()[0]

        # Insert into the ticket table
        cursor.execute('''
                       INSERT INTO tickets (user_name, device_id, device_type, issue_description, date_reported)
                       VALUES (%s, %s, %s, %s, %s)
                       ''', (user_name, device_id, device_type, issue_description, date_reported))

        conn.commit()
        cursor.close()
        conn.close()

        # HTMX or full redirect
        if request.headers.get('HX-Request'):
            return render_template('partials/confirmation.html', device_code=device_code)
        return redirect(url_for('troubleshooting.confirmation', code=device_code))

    cursor.close()
    conn.close()

    # GET Request — serve partial or full form
    if request.headers.get('HX-Request'):
        return render_template('partials/add_ticket.html')
    return render_template('add_ticket.html')

@troubleshooting_bp.route('/delete/<int:id>', methods=('POST',))
@login_required
@roles_required('admin', 'support')
def delete_ticket(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tickets WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Ticket deleted successfully!', 'success')
    return redirect(url_for('troubleshooting.troubleshooting_dashboard'))

@troubleshooting_bp.route('/confirmation')
def confirmation():
    code = request.args.get('code')
    return render_template('partials/confirmation.html', device_code=code)


@troubleshooting_bp.route('/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'support')
def edit_ticket(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Fetch tickets table
    cursor.execute('''
                   SELECT * 
                   FROM tickets 
                   WHERE id = %s''', (id,))
    ticket = cursor.fetchone()

    if not ticket:
        cursor.close()
        conn.close()
        flash("Ticket not found.", "danger")
        return redirect(url_for('troubleshooting.troubleshooting_dashboard'))

    # Fetch devices table
    cursor.execute('''
                   SELECT * 
                   FROM devices 
                   WHERE device_id = %s''', (ticket['device_id'],))
    device = cursor.fetchone()

    if not device:
        cursor.close()
        conn.close()
        flash("Linked device record not found.", "danger")
        return redirect(url_for('troubleshooting.troubleshooting_dashboard'))

    if request.method == 'POST':
        due_date_raw = request.form['due_date']
        due_date = due_date_raw if due_date_raw else None
        assigned_to = request.form['assigned_to'] or None

        new_device_type = request.form['device_type']
        cursor.execute('SELECT device_type, device_code FROM devices WHERE device_id = %s', (ticket['device_id'],))
        current_device = cursor.fetchone()

        # If device type changed, generate a new code
        if new_device_type != current_device['device_type']:
            prefix_map = {
                'Desktop': 'PC', 'Laptop': 'LP', 'Mobile': 'PH',
                'Printer': 'PR', 'Router': 'RT', 'Switch': 'SW',
                'Tablet': 'TB', 'Other': 'OT'
            }
            new_prefix = prefix_map.get(new_device_type, 'OT')
            cursor.execute(
                "SELECT device_code FROM devices WHERE device_code ILIKE %s ORDER BY device_code DESC LIMIT 1",
                (new_prefix + '%',))
            last = cursor.fetchone()

            if last:
                last_number = int(last['device_code'][len(new_prefix):])
                new_number = last_number + 1
            else:
                new_number = 1

            new_code = f"{new_prefix}{new_number:04}"
            cursor.execute('''
                           UPDATE devices
                           SET device_code = %s,
                               device_type = %s
                           WHERE device_id = %s
                           ''', (new_code, new_device_type, ticket['device_id']))
            flash(f'Device type changed. Device code updated to {new_code}.', 'info')
        else:
            cursor.execute('''
                           UPDATE devices
                           SET device_type = %s
                           WHERE device_id = %s
                           ''', (new_device_type, ticket['device_id']))

        # Update ticket info
        cursor.execute('''
                       UPDATE tickets
                       SET user_name         = %s,
                           device_type       = %s,
                           issue_description = %s,
                           troubleshooting   = %s,
                           status            = %s,
                           priority          = %s,
                           category          = %s,
                           assigned_to       = %s,
                           due_date          = %s,
                           last_updated      = CURRENT_TIMESTAMP
                       WHERE id = %s
                       ''', (
                            request.form['user_name'],
                            request.form['device_type'],
                            request.form['issue_description'],
                            request.form['troubleshooting'],
                            request.form['status'],
                            request.form['priority'],
                            request.form['category'],
                            assigned_to,
                            due_date,
                            id
        ))

        # Update device info
        cursor.execute('''
                       UPDATE devices
                       SET hostname         = %s,
                           ipv4_addresses   = %s,
                           ipv6_addresses   = %s,
                           mac_addresses    = %s,
                           network_adapters = %s,
                           os_name          = %s,
                           os_version       = %s,
                           manufacturer     = %s,
                           device_model     = %s,
                           serial_number    = %s
                       WHERE device_id = %s
                       ''', (
                           request.form['hostname'],
                           request.form['ipv4_addresses'],
                           request.form['ipv6_addresses'],
                           request.form['mac_addresses'],
                           request.form['network_adapters'],
                           request.form['os_name'],
                           request.form['os_version'],
                           request.form['manufacturer'],
                           request.form['device_model'],
                           request.form['serial_number'],
                           ticket['device_id']
                       ))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Troubleshooting and device info updated successfully!", "success")
        return redirect(url_for('troubleshooting.troubleshooting_dashboard'))

    cursor.close()
    conn.close()
    return render_template('edit_ticket.html', ticket=ticket, device=device)
