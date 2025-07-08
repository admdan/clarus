from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .db import get_db_connection
from .profile_utils import (
    create_empty_profile_if_missing,
    update_user_profile,
    get_user_profile,
    update_user_pii,
    get_user_pii,
    update_user_employment,
    get_user_employment
)

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def view_profile():
    # Ensure the user profile records exist
    create_empty_profile_if_missing(current_user.id)

    profile_data = get_full_profile(current_user.id)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT * FROM assets
        WHERE assigned_to = %s
        ORDER BY asset_id DESC
    ''', (current_user.id,))
    assigned_assets = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('profile.html', assigned_assets=assigned_assets, profile=profile_data)

def get_full_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user_profile WHERE user_id = %s", (user_id,))
    basic = cursor.fetchone()

    cursor.execute("SELECT * FROM user_pii WHERE user_id = %s", (user_id,))
    pii = cursor.fetchone()

    cursor.execute("SELECT * FROM user_employment WHERE user_id = %s", (user_id,))
    employment = cursor.fetchone()

    cursor.execute("SELECT * FROM user_banking WHERE user_id = %s", (user_id,))
    bank = cursor.fetchone()

    cursor.execute("SELECT * FROM user_family WHERE user_id = %s", (user_id,))
    family = cursor.fetchone()

    cursor.execute("SELECT * FROM user_children WHERE user_id = %s", (user_id,))
    children = cursor.fetchall()

    cursor.execute("SELECT * FROM user_vehicles WHERE user_id = %s", (user_id,))
    vehicle = cursor.fetchone()

    cursor.execute("SELECT * FROM user_documents WHERE user_id = %s", (user_id,))
    documents = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        'basic': basic,
        'pii': pii,
        'employment': employment,
        'bank': bank,
        'family': family,
        'children': children,
        'vehicle': vehicle,
        'documents': documents
    }

@profile_bp.route('/basic')
@login_required
def basic_info():
    # Fetch user profile data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_profile WHERE user_id = %s", (current_user.id,))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile_sections/basic_info.html', profile=profile)

@profile_bp.route('/edit_basic_info', methods=['GET'])
@login_required
def edit_basic_info():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_profile WHERE user_id = %s", (current_user.id,))
    profile_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile_sections/edit_basic_info.html', profile=profile_data)

@profile_bp.route('/update_basic_info', methods=['POST'])
@login_required
def update_basic_info():
    # Collect basic info form data
    form_data = {
        'full_name': request.form.get('full_name') or None,
        'date_of_birth': request.form.get('date_of_birth') or None,
        'gender': request.form.get('gender') or None,
        'contact_number': request.form.get('contact_number') or None,
        'address': request.form.get('address') or None,
    }
    update_user_profile(current_user.id, form_data)
    updated_profile = get_user_profile(current_user.id)
    return render_template('profile_sections/basic_info.html', profile=updated_profile)

@profile_bp.route('/pii')
@login_required
def pii_info():
    # Fetch user PII data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_pii WHERE user_id = %s", (current_user.id,))
    pii = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('profile_sections/pii_info.html', pii=pii)

@profile_bp.route('/edit_pii_info', methods=['GET'])
@login_required
def edit_pii_info():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_pii WHERE user_id = %s", (current_user.id,))
    pii_data = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('profile_sections/edit_pii_info.html', pii=pii_data)

@profile_bp.route('/update_pii_info', methods=['POST'])
@login_required
def update_pii_info():
    # Collect PII form data
    form_data = {
        'id_type': request.form.get('id_type') or None,
        'id_number': request.form.get('id_number') or None,
        'citizenship': request.form.get('citizenship') or None,
        'emergency_contact_name': request.form.get('emergency_contact_name') or None,
        'emergency_contact_number': request.form.get('emergency_contact_number') or None,
        'emergency_contact_address': request.form.get('emergency_contact_address') or None,
    }
    # Update the user_pii table
    update_user_pii(current_user.id, form_data)
    updated_pii = get_user_pii(current_user.id)

    return render_template('profile_sections/pii_info.html', pii=updated_pii)

@profile_bp.route('/employment')
@login_required
def employment_info():
    # Fetch employment info
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_employment WHERE user_id = %s", (current_user.id,))
    employment = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('profile_sections/employment_info.html', employment=employment)

@profile_bp.route('/edit_employment_info', methods=['GET'])
@login_required
def edit_employment_info():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_employment WHERE user_id = %s", (current_user.id,))
    employment_data = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('profile_sections/edit_employment_info.html', employment=employment_data)

@profile_bp.route('/update_employment_info', methods=['POST'])
@login_required
def update_employment_info():
    # Collect employment data
    form_data = {
        'job_title': request.form.get('job_title') or None,
        'department': request.form.get('department') or None,
        'work_email': request.form.get('work_email') or None,
        'date_joined': request.form.get('date_joined') or None,
        'employment_status': request.form.get('employment_status') or None,
        'supervisor': request.form.get('supervisor') or None,
    }
    update_user_employment(current_user.id, form_data)
    updated_employment = get_user_employment(current_user.id)

    return render_template('profile_sections/employment_info.html', employment=updated_employment)
