from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .db import get_db_connection
from .profile_utils import create_empty_profile_if_missing, update_basic_profile_info, get_user_profile

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

@profile_bp.route('/edit_basic_info')
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
    print("HTMX POST triggered!") # Print to see if it hits the route
    # Collect form data
    full_name = request.form.get('full_name') or None
    date_of_birth = request.form.get('date_of_birth') or None
    gender = request.form.get('gender') or None
    contact_number = request.form.get('contact_number') or None
    address = request.form.get('address') or None


    # Update the profile table
    update_basic_profile_info(
        user_id=current_user.id,
        full_name=full_name,
        date_of_birth=date_of_birth,
        gender=gender,
        contact_number=contact_number,
        address=address
    )

    updated_profile = get_user_profile(current_user.id)

    return render_template('profile_sections/basic_info.html', profile=updated_profile)