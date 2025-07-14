from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from .db import get_db_connection
from .profile_utils import (
    create_empty_profile_if_missing,
    update_user_profile, get_user_profile,
    update_user_pii, get_user_pii,
    update_user_employment, get_user_employment,
    update_user_banking, get_user_banking,
    update_user_vehicle, get_user_vehicles, get_vehicle_by_id, delete_user_vehicle, add_user_vehicle,
    update_user_family, get_user_family,
    get_user_spouses, add_user_spouse, update_user_spouse, delete_user_spouse,
    get_user_dependents, add_user_dependent, update_user_dependent, delete_user_dependent

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

    cursor1 = conn.cursor(dictionary=True)
    cursor1.execute("SELECT * FROM user_profile WHERE user_id = %s", (user_id,))
    basic = cursor1.fetchone()
    cursor1.close()

    cursor2 = conn.cursor(dictionary=True)
    cursor2.execute("SELECT * FROM user_pii WHERE user_id = %s", (user_id,))
    pii = cursor2.fetchone()
    cursor2.close()

    cursor3 = conn.cursor(dictionary=True)
    cursor3.execute("SELECT * FROM user_employment WHERE user_id = %s", (user_id,))
    employment = cursor3.fetchone()
    cursor3.close()

    cursor4 = conn.cursor(dictionary=True)
    cursor4.execute("SELECT * FROM user_banking WHERE user_id = %s", (user_id,))
    bank = cursor4.fetchone()
    cursor4.close()

    cursor5 = conn.cursor(dictionary=True)
    cursor5.execute("SELECT * FROM user_family WHERE user_id = %s", (user_id,))
    family = cursor5.fetchone()
    cursor5.close()

    cursor6 = conn.cursor(dictionary=True)
    cursor6.execute("SELECT * FROM user_spouses WHERE user_id = %s", (user_id,))
    spouses = cursor6.fetchall()
    cursor6.close()

    cursor7 = conn.cursor(dictionary=True)
    cursor7.execute("SELECT * FROM user_dependents WHERE user_id = %s", (user_id,))
    dependents = cursor7.fetchall()
    cursor7.close()

    cursor8 = conn.cursor(dictionary=True)
    cursor8.execute("SELECT * FROM user_vehicles WHERE user_id = %s", (user_id,))
    vehicles = cursor8.fetchall()
    cursor8.close()

    cursor9 = conn.cursor(dictionary=True)
    cursor9.execute("SELECT * FROM user_documents WHERE user_id = %s", (user_id,))
    documents = cursor9.fetchone()
    cursor9.close()

    conn.close()

    return {
        'basic': basic,
        'pii': pii,
        'employment': employment,
        'bank': bank,
        'family': family,
        'spouses': spouses,
        'dependents': dependents,
        'vehicles': vehicles,
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

@profile_bp.route('/banking')
@login_required
def banking_info():
    # Fetch banking info
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_banking WHERE user_id = %s", (current_user.id,))
    banking = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('profile_sections/banking_info.html', banking=banking)

@profile_bp.route('/edit_banking_info', methods=['GET'])
@login_required
def edit_banking_info():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_banking WHERE user_id = %s", (current_user.id,))
    banking_data = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('profile_sections/edit_banking_info.html', banking=banking_data)

@profile_bp.route('/update_banking_info', methods=['POST'])
@login_required
def update_banking_info():
    # Collect banking data
    form_data = {
        'bank_name': request.form.get('bank_name') or None,
        'bank_account_number': request.form.get('bank_account_number') or None,
        'account_holder_name': request.form.get('account_holder_name') or None,
    }
    update_user_banking(current_user.id, form_data)
    updated_banking = get_user_banking(current_user.id)

    return render_template('profile_sections/banking_info.html', banking=updated_banking)

@profile_bp.route('/vehicles')
@login_required
def vehicles_info():
    # Fetch vehicle info
    vehicles=get_user_vehicles(current_user.id)
    return render_template('profile_sections/vehicles_info.html', vehicles=vehicles)


@profile_bp.route('/add_vehicle_info', methods=['GET', 'POST'])
@login_required
def add_vehicles_info():
    if request.method == 'POST':
        form_data = {
            'vehicle_type': request.form.get('vehicle_type') or None,
            'make': request.form.get('make') or None,
            'model': request.form.get('model') or None,
            'year_model': request.form.get('year_model') or None,
            'plate_number': request.form.get('plate_number') or None,
            'color': request.form.get('color') or None,
            'parking_permit_id': request.form.get('parking_permit_id') or None
        }
        add_user_vehicle(current_user.id, form_data)
        vehicles = get_user_vehicles(current_user.id)
        return render_template('profile_sections/vehicles_info.html', vehicles=vehicles)

    return render_template('profile_sections/edit_vehicles_info.html', vehicle=None)

@profile_bp.route('/edit_vehicles_info/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicles_info(vehicle_id):
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle or vehicle['user_id'] != current_user.id:
        abort(403)

    if request.method == 'POST':
        form_data = {
            'vehicle_type': request.form.get('vehicle_type') or None,
            'make': request.form.get('make') or None,
            'model': request.form.get('model') or None,
            'year_model': request.form.get('year_model') or None,
            'plate_number': request.form.get('plate_number') or None,
            'color': request.form.get('color') or None,
            'parking_permit_id': request.form.get('parking_permit_id') or None
        }
        update_user_vehicle(vehicle_id, form_data)
        vehicles = get_user_vehicles(current_user.id)
        return render_template('profile_sections/vehicles_info.html', vehicles=vehicles)

    return render_template('profile_sections/edit_vehicles_info.html', vehicle=vehicle)

@profile_bp.route('/delete_vehicle_info/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicles_info(vehicle_id):
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle or vehicle['user_id'] != current_user.id:
        abort(403)

    delete_user_vehicle(vehicle_id)
    vehicles = get_user_vehicles(current_user.id)

    return render_template('profile_sections/vehicles_info.html', vehicles=vehicles)

@profile_bp.route('/family')
@login_required
def family_info():
    family = get_user_family(current_user.id)
    spouses = get_user_spouses(current_user.id)
    dependents = get_user_dependents(current_user.id)
    return render_template(
        'profile_sections/family_info.html',
        family=family,
        spouses=spouses,
        dependents=dependents
    )


@profile_bp.route('/edit_family_info', methods=['GET'])
@login_required
def edit_family_info():
    family_data = get_user_family(current_user.id)
    return render_template('profile_sections/edit_family_info.html', family=family_data)

@profile_bp.route('/update_family_info', methods=['POST'])
@login_required
def update_family_info():
    form_data = {
        'marital_status': request.form.get('marital_status') or None,
    }
    update_user_family(current_user.id, form_data)
    family_data = {
        'family': get_user_family(current_user.id),
        'spouses': get_user_spouses(current_user.id),
        'dependents': get_user_dependents(current_user.id)
    }
    return render_template('profile_sections/family_info.html', **family_data)

@profile_bp.route('/add_spouse_info', methods=['GET', 'POST'])
@login_required
def add_spouse_info():
    if request.method == 'POST':
        form_data = {
            'spouse_name': request.form.get('spouse_name'),
            'spouse_id_type': request.form.get('spouse_id_type'),
            'spouse_id_number': request.form.get('spouse_id_number'),
            'spouse_address': request.form.get('spouse_address')
        }
        add_user_spouse(current_user.id, form_data)
        family_data = {
            'family': get_user_family(current_user.id),
            'spouses': get_user_spouses(current_user.id),
            'dependents': get_user_dependents(current_user.id)
        }
        return render_template('profile_sections/family_info.html', **family_data)
    return render_template('/profile_sections/edit_spouse_info.html', spouse=None)

@profile_bp.route('/edit_spouse_info/<int:spouse_id>', methods=['GET', 'POST'])
@login_required
def edit_spouse_info(spouse_id):
    if request.method == 'POST':
        form_data = {
            'spouse_name': request.form.get('spouse_name'),
            'spouse_id_type': request.form.get('spouse_id_type'),
            'spouse_id_number': request.form.get('spouse_id_number'),
            'spouse_address': request.form.get('spouse_address')
        }
        update_user_spouse(spouse_id, form_data)
        family_data = {
            'family': get_user_family(current_user.id),
            'spouses': get_user_spouses(current_user.id),
            'dependents': get_user_dependents(current_user.id)
        }
        return render_template('profile_sections/family_info.html', **family_data)
    spouses = get_user_spouses(current_user.id)
    spouse = next((s for s in spouses if s['id'] == spouse_id), None)
    return render_template('profile_sections/edit_spouse_info.html', spouse=spouse)

@profile_bp.route('/delete_spouse_info/<int:spouse_id>', methods=['POST'])
@login_required
def delete_spouse_info(spouse_id):
    delete_user_spouse(spouse_id)
    family_data = {
        'family': get_user_family(current_user.id),
        'spouses': get_user_spouses(current_user.id),
        'dependents': get_user_dependents(current_user.id)
    }
    return render_template('profile_sections/family_info.html', **family_data)

@profile_bp.route('/add_dependent_info', methods=['GET', 'POST'])
@login_required
def add_dependent_info():
    if request.method == 'POST':
        form_data = {
            'dependent_name': request.form.get('dependent_name'),
            'dependent_relationship': request.form.get('dependent_relationship'),
            'dependent_birthdate': request.form.get('dependent_birthdate'),
            'dependent_notes': request.form.get('dependent_notes')
        }
        add_user_dependent(current_user.id, form_data)
        family_data = {
            'family': get_user_family(current_user.id),
            'spouses': get_user_spouses(current_user.id),
            'dependents': get_user_dependents(current_user.id)
        }
        return render_template('profile_sections/family_info.html', **family_data)
    return render_template('profile_sections/edit_dependent_info.html', dependent=None)

@profile_bp.route('/edit_dependent_info/<int:dependent_id>', methods=['GET', 'POST'])
@login_required
def edit_dependent_info(dependent_id):
    if request.method == 'POST':
        form_data = {
            'dependent_name': request.form.get('dependent_name'),
            'dependent_relationship': request.form.get('dependent_relationship'),
            'dependent_birthdate': request.form.get('dependent_birthdate'),
            'dependent_notes': request.form.get('dependent_notes')
        }
        update_user_dependent(dependent_id, form_data)
        family_data = {
            'family': get_user_family(current_user.id),
            'spouses': get_user_spouses(current_user.id),
            'dependents': get_user_dependents(current_user.id)
        }
        return render_template('profile_sections/family_info.html', **family_data)

    dependents = get_user_dependents(current_user.id)
    dependent = next((d for d in dependents if d['id'] == dependent_id), None)
    return render_template('profile_sections/edit_dependent_info.html', dependent=dependent)

@profile_bp.route('/delete_dependent_info/<int:dependent_id>', methods=['POST'])
@login_required
def delete_dependent_info(dependent_id):
    delete_user_dependent(dependent_id)
    family_data = {
        'family': get_user_family(current_user.id),
        'spouses': get_user_spouses(current_user.id),
        'dependents': get_user_dependents(current_user.id)
    }
    return render_template('profile_sections/family_info.html', **family_data)