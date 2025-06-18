# app/troubleshooting.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_db_connection
from datetime import datetime

troubleshooting_bp = Blueprint('troubleshooting', __name__, url_prefix='/troubleshooting')

@troubleshooting_bp.route('/', methods=['GET'])
def troubleshooting_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Always fetch 5 most recently updated tickets
    cursor.execute('''SELECT id, issue_description, last_updated 
                      FROM tickets 
                      ORDER BY last_updated DESC 
                      LIMIT 5''')
    recently_updated = cursor.fetchall()

    # Filters
    query = request.args.get('query', '').strip()
    status_filter = request.args.get('status', 'All')

    sql = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if query:
        sql += " AND (user_name LIKE %s OR device_id LIKE %s OR issue_description LIKE %s)"
        q = f"%{query}%"
        params += [q, q, q]

    if status_filter != 'All':
        sql += " AND status = %s"
        params.append(status_filter)

    sql += " ORDER BY last_updated DESC"
    cursor.execute(sql, params)
    filtered_tickets = cursor.fetchall()

    conn.close()

    return render_template('troubleshooting.html',
                           tickets=filtered_tickets,
                           recently_updated=recently_updated,
                           query=query,
                           selected_status=status_filter)

@troubleshooting_bp.route('/<int:id>', methods=['GET', 'POST'])
def handle_troubleshooting(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''SELECT * FROM tickets 
                      WHERE id = %s''', (id,))
    ticket = cursor.fetchone()

    if request.method == 'POST':
        troubleshooting = request.form['troubleshooting']
        status = request.form['status']
        cursor.execute('''UPDATE tickets 
                          SET troubleshooting = %s, status = %s, last_updated = %s
                          WHERE id = %s''',
                       (troubleshooting, status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id))
        conn.commit()
        conn.close()
        flash("Troubleshooting updated successfully!", "success")
        return redirect(url_for('troubleshooting.troubleshooting_dashboard'))

    conn.close()
    return render_template('troubleshooting_edit.html', ticket=ticket)
