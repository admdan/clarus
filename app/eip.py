import psycopg2.extras
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .db import get_db_connection
from .routes import roles_required
from datetime import datetime
from .profile_utils import create_empty_profile_if_missing

eip_bp = Blueprint('eip', __name__, url_prefix='/eip')

@eip_bp.route('/')
@login_required
@roles_required('admin', 'hr', 'support')
def eip_dashboard():
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    status_filter = request.args.get('status')
    search_query = request.args.get('search')

    conditions = []
    params = []

    if status_filter:
        conditions.append("cr.status = %s")
        params.append(status_filter)

    if search_query:
        conditions.append("(u.username ILIKE %s OR u.email ILIKE %s)")
        like_value = f"%{search_query}%"
        params.extend([like_value, like_value])

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    count_query = f"""
        SELECT COUNT(*) AS total
        FROM change_requests cr
        JOIN users u ON cr.user_id = u.id
        {where_clause}
    """
    cursor.execute(count_query, params)
    total_requests = cursor.fetchone()['total']
    total_pages = (total_requests + per_page - 1) // per_page

    # Main query for paginated data
    main_query = f"""
        SELECT cr.id, 
               u.id AS user_id,
               u.username,
               u.email,
               cr.field_requested,
               cr.new_value,
               cr.note,
               cr.timestamp,
               cr.status,
               cr.resolved_at,
               cr.admin_note,
               r.username AS resolved_by
        FROM change_requests cr
        JOIN users u ON cr.user_id = u.id
        LEFT JOIN users r ON cr.resolved_by = r.id
        {where_clause}
        ORDER BY cr.timestamp DESC
        LIMIT %s OFFSET %s
    """
    params.extend([per_page, offset])
    cursor.execute(main_query, params)
    change_requests = cursor.fetchall()

    cursor.close()
    conn.close()

    if request.headers.get('HX-Request'):
        return render_template(
            'partials/eip_table.html',
            change_requests=change_requests,
            current_page=page,
            total_pages=total_pages,
            status_filter=status_filter,
            search_query=search_query
        )
    else:
        return render_template(
            'eip.html',
            change_requests=change_requests,
            current_page=page,
            total_pages=total_pages,
            status_filter=status_filter,
            search_query=search_query
        )

@eip_bp.route('/approve/<int:request_id>', methods=['POST'])
@login_required
@roles_required('admin', 'hr', 'support')
def approve_change_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get a change request
    cursor.execute("SELECT * FROM change_requests WHERE id = %s", (request_id,))
    req = cursor.fetchone()

    if not req or req['status'] != 'Pending':
        flash("Invalid or already processed request.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('eip.eip_dashboard'))

    field = req['field_requested']
    value = req['new_value']
    user_id = req['user_id']

    # ───── FIELD MAPPING ─────
    field_map = {
        # ─ BASIC INFO ─
        "Full Name": ("user_profile", "full_name"),
        "Date of Birth": ("user_profile", "date_of_birth"),
        "Gender": ("user_profile", "gender"),
        "Contact Number": ("user_profile", "contact_number"),
        "Address": ("user_profile", "address"),

        # ─ PII ─
        "ID Type": ("user_pii", "id_type"),
        "ID Number": ("user_pii", "id_number"),
        "Citizenship": ("user_pii", "citizenship"),
        "Emergency Contact Name": ("user_pii", "emergency_contact_name"),
        "Emergency Contact Number": ("user_pii", "emergency_contact_number"),
        "Emergency Contact Address": ("user_pii", "emergency_contact_address"),

        # ─ EMPLOYMENT ─
        "Job Title": ("user_employment", "job_title"),
        "Department": ("user_employment", "department"),
        "Work Email": ("user_employment", "work_email"),
        "Date Joined": ("user_employment", "date_joined"),
        "Employment Status": ("user_employment", "employment_status"),
        "Supervisor": ("user_employment", "supervisor"),

        # ─ BANKING ─
        "Bank Name": ("user_banking", "bank_name"),
        "Bank Account Number": ("user_banking", "bank_account_number"),
        "Account Holder Name": ("user_banking", "account_holder_name"),

        # ─ VEHICLE ─
        "Plate Number": ("user_vehicles", "plate_number"),
        "Parking Permit ID": ("user_vehicles", "parking_permit_id")
    }

    if field not in field_map:
        flash(f"Field '{field}' is not supported for auto-update.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for('eip.eip_dashboard'))

    table, column = field_map[field]

    # ───── VALIDATION ─────
    if column == 'date_of_birth':
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            flash("Date must be in YYYY-MM-DD format.", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('eip.eip_dashboard'))

    # ───── EXECUTE UPDATE ─────
    try:
        if table in {'user_profile', 'user_pii', 'user_employment', 'user_banking', 'user_family'}:
            create_empty_profile_if_missing(user_id)

        if table == 'user_vehicles':
            cursor.execute("SELECT COUNT(*) AS total FROM user_vehicles WHERE user_id = %s", (user_id,))
            vehicle_count = cursor.fetchone()['total']
            if vehicle_count != 1:
                flash(
                    "Vehicle change requests need manual review when a user has multiple vehicle records.",
                    "warning"
                )
                return redirect(url_for('eip.eip_dashboard'))

        cursor.execute(
            f"""
            UPDATE {table}
            SET {column} = %s,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = %s
            """,
            (value, user_id)
        )

        if cursor.rowcount == 0:
            raise ValueError(f"No matching record found for {table}.{column}")

        # Update change_requests status
        cursor.execute("""
            UPDATE change_requests
            SET status      = 'Approved',
                resolved_at = NOW(),
                admin_note  = %s,
                resolved_by = %s
            WHERE id = %s
        """, (f"Auto-applied to {table}.{column}", current_user.id, request_id))

        conn.commit()
        flash("Change approved and applied successfully.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error applying change: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('eip.eip_dashboard'))

@eip_bp.route('/decline/<int:request_id>', methods=['POST'])
@login_required
@roles_required('admin', 'hr', 'support')
def decline_change_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE change_requests
        SET status      = 'Declined',
            resolved_at = NOW(),
            admin_note  = 'Declined by admin',
            resolved_by = %s
        WHERE id = %s
    """, (current_user.id, request_id))

    conn.commit()
    cursor.close()
    conn.close()
    flash("Change request declined.", "info")
    return redirect(url_for('eip.eip_dashboard'))
