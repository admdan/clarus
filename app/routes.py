from flask import Blueprint, render_template, request, redirect, url_for
from .db import get_db_connection
from datetime import datetime
from flask import flash

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''SELECT * FROM tickets''')
    tickets = cursor.fetchall()
    conn.close()
    return render_template('index.html', tickets=tickets)

@bp.route('/add', methods=('GET', 'POST'))
def add_ticket():
    if request.method == 'POST':
        user_name = request.form['user_name']
        device_id = request.form['device_id']
        issue_description = request.form['issue_description']
        date_reported = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO tickets (user_name, device_id, issue_description, date_reported) 
               VALUES (%s, %s, %s, %s)''',
            (user_name, device_id, issue_description, date_reported)
        )
        conn.commit()
        conn.close()
        flash("Ticket added successfully!", "success")
        return redirect(url_for('routes.index'))
    return render_template('add_ticket.html')

@bp.route('/update/<int:id>', methods=('GET', 'POST'))
def update_ticket(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''SELECT * FROM tickets
                      WHERE id = %s''', (id,))
    ticket = cursor.fetchone()
    if request.method == 'POST':
        troubleshooting = request.form['troubleshooting']
        status = request.form['status']
        cursor.execute(
            '''
            UPDATE tickets 
            SET troubleshooting = %s, status = %s, last_updated= %s
            WHERE id = %s''',
            (troubleshooting, status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id)
        )
        conn.commit()
        conn.close()
        flash("Ticket updated successfully!", "success")
        return redirect(url_for('routes.index'))
    conn.close()
    return render_template('update_ticket.html', ticket=ticket)

@bp.route('/delete/<int:id>', methods=('POST',))
def delete_ticket(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM tickets 
                      WHERE id = %s''', (id,))
    conn.commit()
    conn.close()
    flash('Ticket deleted successfully!', 'success')
    return redirect(url_for('routes.index'))




