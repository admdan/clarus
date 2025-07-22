from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .db import get_db_connection
from .routes import roles_required
from datetime import datetime
from .profile_utils import update_field_and_timestamp

eip_bp = Blueprint('eip', __name__, url_prefix='/eip')

@eip_bp.route('/')
@login_required
@roles_required('admin', 'hr', 'support')
def eip_dashboard():
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total count for pagination
    cursor.execute("SELECT COUNT(*) AS total FROM change_requests")
    total_requests = cursor.fetchone()['total']
    total_pages = (total_requests + per_page - 1) // per_page

    cursor.execute("""
                   SELECT cr.id,
                          u.id       AS user_id,
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
                   ORDER BY cr.timestamp DESC
                   LIMIT %s OFFSET %s
                   """, (per_page, offset))

    change_requests = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'eip.html',
        change_requests=change_requests,
        current_page=page,
        total_pages=total_pages
    )


@eip_bp.route('/approve/<int:request_id>', methods=['POST'])
@login_required
@roles_required('admin', 'hr', 'support')
def approve_change_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get a change request
    cursor.execute("SELECT * FROM change_requests WHERE id = %s", (request_id,))
    req = cursor.fetchone()

    if not req or req['status'] != 'Pending':
        flash("Invalid or already processed request.", "danger")
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
        return redirect(url_for('eip.eip_dashboard'))

    table, column = field_map[field]

    # ───── VALIDATION ─────
    if column == 'date_of_birth':
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            flash("Date must be in YYYY-MM-DD format.", "danger")
            return redirect(url_for('eip.eip_dashboard'))

    # ───── EXECUTE UPDATE ─────
    try:
        # Apply the value + timestamp in one go
        update_field_and_timestamp(table, column, value, user_id)

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
