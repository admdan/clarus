from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .db import get_db_connection
from .routes import roles_required

role = Blueprint('role', __name__)


@role.route('/update-role/<int:user_id>', methods=['POST'])
@login_required
@roles_required('admin')
def update_role(user_id):
    new_role = request.form.get('role')
    if new_role not in ['basic', 'support', 'hr', 'admin']:
        return "Invalid role", 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
    conn.commit()

    # fetch updated user to re-render a row
    cursor.execute("SELECT id, username, email, role, created_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('partials/user_row.html', user=user)

    flash('Role updated successfully.', 'success')
    return redirect(url_for('routes.manage_role'))

@role.route('/search-users', methods=['GET'])
@login_required
@roles_required('admin')
def search_users():
    query = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()
    sort = request.args.get('sort', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    base_query = "SELECT id, username, email, role, created_at FROM users WHERE 1=1"
    params = []

    if query:
        base_query += " AND (username LIKE %s OR email LIKE %s)"
        params += [f"%{query}%", f"%{query}%"]

    if role_filter and role_filter in ['basic', 'support', 'hr', 'admin']:
        base_query += " AND role = %s"
        params.append(role_filter)

    # Handle sorting by role (default ASC)
    if sort == 'role':
        base_query += " ORDER BY role ASC"

    cursor.execute(base_query, tuple(params))
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return f'<div id="users-table-wrapper">{ render_template("partials/user_table.html", users=users) }</div>'
